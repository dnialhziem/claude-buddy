"""
classifier.py — Email classification using Ollama (individual + parallel mode)
Pre-filters obvious junk without hitting Ollama, then classifies remainder in parallel.
"""

import json
import logging
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OLLAMA_URL: str = "http://localhost:11434/api/generate"
MODEL: str = "mistral:7b"
TIMEOUT: int = 120
MAX_WORKERS: int = 3  # parallel Ollama calls

# ── Pre-filter rules — instant LOW, no Ollama call ───────────────────────────

# Senders whose emails are always low priority
LOW_SENDERS = {
    "messages-noreply@linkedin.com",       # LinkedIn suggestions/analytics (NOT message digests)
    "jobs-listings@linkedin.com",
    "inmail-hit-reply@linkedin.com",
    "notifications-noreply@linkedin.com",
    "jobalerts-noreply@linkedin.com",
    "news-noreply@linkedin.com",
    "hit-reply@linkedin.com",
}

# Sender domain patterns → always LOW
LOW_SENDER_DOMAINS = [
    "mailer.kmart.com.au",
    "email.grab.com",
    "mail.shopee.com.my",
    "deals.foodpanda.com",
    "iqiyi.com",
    "mailer.grab.com",
    "match.indeed.com",
    "indeed.com",
    "jobstreet.com",
    "seek.com.au",
    # linkedin.com excluded — messaging-digest-noreply@linkedin.com needs Ollama
    "mail.anthropic.com",
    "notifications.google.com",
]

# Subject keywords → always LOW (case-insensitive)
LOW_SUBJECT_KEYWORDS = [
    "unsubscribe",
    "% off",
    "% discount",
    "limited time offer",
    "don't miss out",
    "your weekly digest",
    "weekly newsletter",
    "your posts got",
    "impressions last week",
    "hiring for barista",
    "similar jobs in your area",
    "your raya",
    "buka plans",
    "kombo jimat",
    "antivirus protection has expired",
]

def _is_obvious_low(subject: str, sender: str) -> bool:
    """Return True if the email can be instantly classified as LOW without Ollama."""
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    if any(addr in sender_lower for addr in LOW_SENDERS):
        return True
    if any(domain in sender_lower for domain in LOW_SENDER_DOMAINS):
        return True
    if any(kw in subject_lower for kw in LOW_SUBJECT_KEYWORDS):
        return True
    return False

BASE_DIR: Path = Path(__file__).resolve().parent
PROMPTS_DIR: Path = BASE_DIR / "prompts"

# State cache to prevent repetitive disk I/O
_PROMPT_CACHE: dict[str, Any] = {"system": None, "examples": None}


def _load_prompts() -> tuple[str, list[dict[str, Any]]]:
    if _PROMPT_CACHE["system"] is not None and _PROMPT_CACHE["examples"] is not None:
        return _PROMPT_CACHE["system"], _PROMPT_CACHE["examples"]

    try:
        system_path = PROMPTS_DIR / "system_prompt.txt"
        examples_path = PROMPTS_DIR / "examples.json"

        _PROMPT_CACHE["system"] = system_path.read_text(encoding="utf-8").strip()
        _PROMPT_CACHE["examples"] = json.loads(examples_path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        logger.error(f"Required prompt file missing: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Malformed examples.json: {e}")
        sys.exit(1)

    return _PROMPT_CACHE["system"], _PROMPT_CACHE["examples"]


def clean_email(raw_text: str, max_words: int = 200) -> str:
    text = BeautifulSoup(raw_text, "html.parser").get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return " ".join(text.split()[:max_words])


def _build_prompt(subject: str, sender: str, preview: str) -> str:
    system, examples = _load_prompts()

    example_block = "\n\n".join(
        f"Example {i+1}:\nInput: {e['input']}\nOutput: {json.dumps(e['output'])}"
        for i, e in enumerate(examples)
    )

    return (
        f"{system}\n\n{example_block}\n\n"
        "Now classify this email. Reply with ONLY the JSON object, nothing else:\n"
        f"Subject: {subject}\nFrom: {sender}\nPreview: {preview}"
    )


FALLBACK: dict[str, Any] = {
    "is_important": False,
    "score": 1,
    "category": "general",
    "reason": "Classification failed."
}


def _build_batch_prompt(emails: list[dict[str, str]]) -> str:
    """Build a single prompt that classifies multiple emails at once."""
    system, examples = _load_prompts()

    example_block = "\n\n".join(
        f"Example {i+1}:\nInput: {e['input']}\nOutput: {json.dumps(e['output'])}"
        for i, e in enumerate(examples[:2])  # limit examples to keep prompt short
    )

    email_block = "\n\n".join(
        f"EMAIL_{i+1}:\nSubject: {e['subject']}\nFrom: {e['sender']}\nPreview: {e['preview']}"
        for i, e in enumerate(emails)
    )

    return (
        f"{system}\n\n{example_block}\n\n"
        f"Classify each email below. Reply with ONLY a JSON array of objects in order, "
        f"one per email, nothing else:\n\n{email_block}"
    )


def _parse_batch(raw: str, count: int) -> list[dict[str, Any]]:
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    results = json.loads(match.group()) if match else json.loads(raw)
    # Normalise categories
    for r in results:
        if isinstance(r.get("category"), list):
            r["category"] = r["category"][0] if r["category"] else "general"
    # Pad with fallbacks if model returned fewer items than expected
    while len(results) < count:
        results.append(dict(FALLBACK))
    return results[:count]


def classify_emails_batch(emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Classify a list of emails in batches. Returns results in the same order."""
    results: list[dict[str, Any]] = []

    for i in range(0, len(emails), BATCH_SIZE):
        batch = emails[i:i + BATCH_SIZE]
        items = [
            {
                "subject": e["subject"],
                "sender": e["from"],
                "preview": clean_email(e["body"]),
            }
            for e in batch
        ]
        prompt = _build_batch_prompt(items)
        logger.info(f"Classifying emails {i+1}–{i+len(batch)} of {len(emails)}...")

        try:
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                # No "format": "json" here — Ollama constrains to object {}, but we need array []
                "options": {"temperature": 0.0},
            }
            resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            batch_results = _parse_batch(resp.json().get("response", ""), len(batch))
            results.extend(batch_results)

        except requests.exceptions.ConnectionError:
            logger.error("Ollama not running. Start it with: ollama serve")
            results.extend([dict(FALLBACK)] * len(batch))
            break
        except requests.exceptions.Timeout:
            logger.error(f"Batch {i//BATCH_SIZE + 1} timed out — falling back to individual classification.")
            # Try one-by-one for this batch as a last resort
            for item in items:
                try:
                    single_prompt = _build_prompt(item["subject"], item["sender"], item["preview"])
                    payload["prompt"] = single_prompt
                    resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
                    match = re.search(r'\{.*\}', resp.json().get("response", ""), re.DOTALL)
                    results.append(json.loads(match.group()) if match else dict(FALLBACK))
                except Exception:
                    results.append(dict(FALLBACK))
        except (json.JSONDecodeError, AttributeError) as e:
            raw_resp = resp.json().get("response", "") if resp else ""
            logger.error(f"Batch {i//BATCH_SIZE + 1} invalid JSON: {e}")
            logger.error(f"Raw response was: {raw_resp[:300]!r}")
            results.extend([dict(FALLBACK)] * len(batch))

    return results


def classify_email(subject: str, sender: str, body: str) -> dict[str, Any]:
    """Classify a single email. Pre-filters obvious junk before hitting Ollama."""
    if _is_obvious_low(subject, sender):
        return {**FALLBACK, "reason": "Pre-filtered: automated/promotional sender or subject."}

    preview = clean_email(body)
    prompt = _build_prompt(subject, sender, preview)

    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.0},
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        raw = resp.json().get("response", "")
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        parsed = json.loads(match.group()) if match else json.loads(raw)
        if isinstance(parsed.get("category"), list):
            parsed["category"] = parsed["category"][0] if parsed["category"] else "general"
        parsed["score"] = int(parsed.get("score", 1))
        return parsed
    except Exception as e:
        logger.error(f"classify_email failed: {e}")
        return dict(FALLBACK)


def classify_emails_parallel(emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Classify emails in parallel. Pre-filters run instantly; remainder hit Ollama concurrently."""
    results: list[dict[str, Any] | None] = [None] * len(emails)
    to_classify: list[tuple[int, dict[str, Any]]] = []

    # Pass 1: pre-filter
    for i, email in enumerate(emails):
        if _is_obvious_low(email["subject"], email["from"]):
            results[i] = {**FALLBACK, "reason": "Pre-filtered: automated/promotional."}
        else:
            to_classify.append((i, email))

    pre_count = len(emails) - len(to_classify)
    if pre_count:
        logger.info(f"Pre-filtered {pre_count} emails instantly.")
    if to_classify:
        logger.info(f"Classifying {len(to_classify)} emails via Ollama ({MAX_WORKERS} parallel)...")

    # Pass 2: parallel Ollama calls for the rest
    def _classify(idx_email: tuple[int, dict[str, Any]]) -> tuple[int, dict[str, Any]]:
        idx, email = idx_email
        return idx, classify_email(email["subject"], email["from"], email["body"])

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_classify, item): item[0] for item in to_classify}
        for future in as_completed(futures):
            idx, result = future.result()
            results[idx] = result

    return [r if r is not None else dict(FALLBACK) for r in results]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    test_emails = [
        {
            "subject": "User, what do you think of this line I wrote for your resume?",
            "from": "kim@resumeworded.com",
            "body": "Here is a suggested resume line for your profile..."
        },
        {
            "subject": "COMP10001 Assignment 2 due Friday",
            "from": "lecturer@unimelb.edu.au",
            "body": "Reminder that Assignment 2 is due this Friday 11:59pm. Please submit via LMS."
        },
        {
            "subject": "user, add Jane Doe",
            "from": "messages-noreply@linkedin.com",
            "body": "Do you know Jane Doe? 22 mutual connections."
        },
    ]

    print("=== Classifier Test ===\n")
    for e in test_emails:
        result = classify_email(e["subject"], e["from"], e["body"])
        flag = "[HIGH]" if result.get("score", 0) >= 7 else "[MED] " if result.get("score", 0) >= 4 else "[LOW] "

        print(f"{flag} Score:{result.get('score', 'N/A')} | {e['subject'][:50]}")
        print(f"        Category: {result.get('category', 'unknown')} | {result.get('reason', 'N/A')}\n")
