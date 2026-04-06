"""
Email Butler CLI
----------------
Usage:
  python butler.py briefing      — Morning email summary
  python butler.py sort          — Sort inbox into labels
  python butler.py correct --email-id ID --correct-label HIGH
  python butler.py audit         — Weekly accuracy report
  python butler.py receipts      — Show all logged receipt emails
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

from classifier import classify_email
from gmail import fetch_unread_emails, move_to_label

BASE_DIR: Path = Path(__file__).resolve().parent
CORRECTIONS_FILE: Path = BASE_DIR / "corrections.csv"
RECEIPTS_FILE: Path = BASE_DIR / "receipts.csv"

LABEL_MAP: dict[str, str] = {
    "deadline": "Butler/Deadlines",
    "university": "Butler/University",
    "newsletter": "Butler/Newsletters",
    "spam": "Butler/Spam-Review",
    "receipt": "Butler/Orders",
    "finance": "Butler/Banking",
    "general": "Butler/Newsletters"
}

SCORE_HIGH: int = 7
SCORE_MED: int = 4

# ── CSV File Operations ──────────────────────────────────────────────────────

def _read_csv(filepath: Path) -> list[dict[str, Any]]:
    if not filepath.exists():
        return []
    with filepath.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(filepath: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with filepath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _append_csv(filepath: Path, fieldnames: list[str], row: dict[str, Any]) -> None:
    file_exists = filepath.exists()
    with filepath.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ── Core Functions ───────────────────────────────────────────────────────────

def log_classification(email_id: str, subject: str, score: int, category: str) -> None:
    _append_csv(
        CORRECTIONS_FILE,
        ["email_id", "subject", "ai_score", "category", "correct_label"],
        {
            "email_id": email_id,
            "subject": subject,
            "ai_score": score,
            "category": category,
            "correct_label": ""
        }
    )


def log_receipt(email_id: str, subject: str, sender: str, date: str) -> None:
    _append_csv(
        RECEIPTS_FILE,
        ["date", "merchant", "subject", "email_id"],
        {
            "date": date,
            "merchant": sender,
            "subject": subject,
            "email_id": email_id
        }
    )


def apply_correction(email_id: str, correct_label: str) -> None:
    rows = _read_csv(CORRECTIONS_FILE)
    updated = False

    for row in rows:
        if row["email_id"] == email_id:
            row["correct_label"] = correct_label
            updated = True
            break

    if not updated:
        print(f"Email ID {email_id} not found in corrections log.")
        return

    _write_csv(
        CORRECTIONS_FILE,
        ["email_id", "subject", "ai_score", "category", "correct_label"],
        rows
    )
    print(f"Correction logged: {email_id} → {correct_label}")


# ── CLI Commands ─────────────────────────────────────────────────────────────

def briefing() -> None:
    print("Fetching emails...\n")
    emails = fetch_unread_emails(count=50)

    if not emails:
        print("No unread emails.")
        return

    classified = []
    for email in emails:
        result = classify_email(email["subject"], email["from"], email["body"])
        result["email"] = email
        classified.append(result)

        log_classification(
            email["id"], email["subject"], result.get("score", 1), result.get("category", "general")
        )
        if result.get("category") == "receipt":
            log_receipt(
                email["id"], email["subject"], email["from"], email["date"]
            )

    classified.sort(key=lambda x: x.get("score", 1), reverse=True)

    important = [c for c in classified if c.get("score", 1) >= SCORE_HIGH]
    medium = [c for c in classified if SCORE_MED <= c.get("score", 1) < SCORE_HIGH]
    low = [c for c in classified if c.get("score", 1) < SCORE_MED]

    print(f"=== Morning Briefing — {len(emails)} unread emails ===\n")

    if important:
        print("--- ACTION REQUIRED ---")
        for c in important:
            print(
                f"[HIGH {c.get('score', 1)}] {c['email']['subject'][:60]}\n"
                f"        From: {c['email']['from'][:50]}\n"
                f"        {c.get('reason', '')}\n"
            )

    if medium:
        print("--- THIS WEEK ---")
        for c in medium:
            print(
                f"[MED  {c.get('score', 1)}] {c['email']['subject'][:60]}\n"
                f"        {c.get('reason', '')}\n"
            )

    print(f"--- LOW PRIORITY ({len(low)} emails) ---")
    for c in low:
        print(f"[LOW  {c.get('score', 1)}] {c['email']['subject'][:60]}")

    print("\nRun 'python butler.py sort' to move emails into labels.")

    _interactive_correction(important + medium + low)


def _interactive_correction(all_classified: list[dict[str, Any]]) -> None:
    high = [c for c in all_classified if c.get("score", 1) >= SCORE_HIGH]
    med  = [c for c in all_classified if SCORE_MED <= c.get("score", 1) < SCORE_HIGH]
    low  = [c for c in all_classified if c.get("score", 1) < SCORE_MED]

    # Build numbered list preserving original order for corrections
    numbered = all_classified

    print("\n--- Flag any misclassifications (Enter to skip) ---")
    print("Format: number=HIGH / number=MED / number=LOW\n")

    if high:
        print("  [HIGH]")
        for c in high:
            i = numbered.index(c) + 1
            print(f"  {i:>2}. {c['email']['subject'][:50]}")
            print(f"       From: {c['email']['from'][:50]}")

    if med:
        print("  [MED]")
        for c in med:
            i = numbered.index(c) + 1
            print(f"  {i:>2}. {c['email']['subject'][:50]}")
            print(f"       From: {c['email']['from'][:50]}")

    if low:
        print(f"  [LOW] ({len(low)} emails)")
        for c in low:
            i = numbered.index(c) + 1
            print(f"  {i:>2}. {c['email']['subject'][:50]}")

    print()
    while True:
        try:
            raw = input("Correction (or Enter to skip): ").strip()
            if not raw:
                break

            num_str, label = raw.split("=")
            idx = int(num_str.strip()) - 1
            label = label.strip().upper()

            if 0 <= idx < len(numbered):
                c = numbered[idx]
                apply_correction(c["email"]["id"], label)
            else:
                print("  Invalid number.")
        except (EOFError, KeyboardInterrupt):
            break
        except (ValueError, KeyError):
            print("  Format: number=LABEL (e.g. 3=LOW)")


def sort_inbox() -> None:
    print("Fetching and sorting emails...\n")
    emails = fetch_unread_emails(count=50)

    if not emails:
        print("No unread emails to sort.")
        return

    for email in emails:
        result = classify_email(email["subject"], email["from"], email["body"])
        score = result.get("score", 1)
        category = result.get("category", "general")

        label = (
            "Butler/Important" if score >= SCORE_HIGH
            else LABEL_MAP.get(category, "Butler/Newsletters")
        )
        move_to_label(email["id"], label)

        flag = "[HIGH]" if score >= SCORE_HIGH else "[MED] " if score >= SCORE_MED else "[LOW] "
        print(f"{flag} → {label}: {email['subject'][:50]}")

    print("\nDone. Check your Gmail labels under 'Butler/'.")


def audit() -> None:
    rows = _read_csv(CORRECTIONS_FILE)
    if not rows:
        print("No data in corrections log yet. Run briefing first.")
        return

    total = len(rows)
    wrong = [
        r for r in rows
        if r["correct_label"] and r["correct_label"] != r["category"]
    ]
    correct_count = total - len(wrong)

    print("\n=== Weekly Accuracy Audit ===")
    print(
        f"Total: {total} | Correct: {correct_count} "
        f"({correct_count / total * 100:.0f}%) | Wrong: {len(wrong)}\n"
    )

    if wrong:
        print("--- Misclassifications ---")
        for r in wrong:
            print(f"  [{r['category']} → {r['correct_label']}] {r['subject'][:60]}")

        # Auto-suggest example fix for most common mistake
        patterns = Counter(
            f"{r['category']}→{r['correct_label']}" for r in wrong
        )
        top_pattern, top_count = patterns.most_common(1)[0]
        top_wrong = next(
            r for r in wrong
            if f"{r['category']}→{r['correct_label']}" == top_pattern
        )
        wrong_cat, right_label = top_pattern.split("→")

        print(f"\n--- Suggested fix (add to examples.json) ---")
        print(f"Most common mistake: {top_pattern} ({top_count}x)\n")
        suggested = {
            "input": (
                f"Subject: {top_wrong['subject']}\n"
                f"From: (sender)\nPreview: (email preview)"
            ),
            "output": {
                "is_important": right_label in ("HIGH", "IMPORTANT"),
                "score": 8 if right_label == "HIGH" else 2,
                "category": right_label.lower(),
                "reason": (
                    f"Corrected: was {wrong_cat}, "
                    f"should be {right_label.lower()}"
                )
            }
        }
        print(json.dumps(suggested, indent=2))
        print(
            "\nCopy the above into prompts/examples.json, "
            "fill in From/Preview, then re-run briefing."
        )
    else:
        print("No corrections logged — all classifications accepted.")


def receipts() -> None:
    rows = _read_csv(RECEIPTS_FILE)
    if not rows:
        print("No receipts logged yet. Run 'briefing' first.")
        return

    print(f"\n=== Orders & Receipts Log ({len(rows)} total) ===\n")
    for r in rows:
        print(f"  [{r['date'][:10]}] {r['merchant'][:40]}\n           {r['subject'][:60]}\n")


# ── CLI Entry Point ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Email Butler — AI-powered Gmail manager"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("briefing", help="Morning email briefing")
    subparsers.add_parser("sort", help="Sort inbox into Gmail labels")

    correct_parser = subparsers.add_parser(
        "correct", help="Log a misclassification correction"
    )
    correct_parser.add_argument("--email-id", required=True)
    correct_parser.add_argument("--correct-label", required=True)

    subparsers.add_parser("audit", help="Weekly accuracy report")
    subparsers.add_parser("receipts", help="Show all logged receipt emails")

    args = parser.parse_args()

    commands = {
        "briefing": briefing,
        "sort": sort_inbox,
        "audit": audit,
        "receipts": receipts,
    }

    if args.command == "correct":
        apply_correction(args.email_id, args.correct_label)
    else:
        commands[args.command]()


if __name__ == "__main__":
    main()
