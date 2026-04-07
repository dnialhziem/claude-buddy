"""
classifier.py — Email classification using Ollama (batch mode)
Cleans email HTML, classifies emails in batches to avoid per-email timeouts.
"""

import json
import logging
import re
import requests
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OLLAMA_URL: str = "http://localhost:11434/api/generate"
MODEL: str = "mistral:7b"
TIMEOUT: int = 120       # per batch request
BATCH_SIZE: int = 5      # emails per Ollama call

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
                "format": "json",
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
        except (json.JSONDecodeError, AttributeError):
            logger.error(f"Batch {i//BATCH_SIZE + 1} returned invalid JSON — skipping.")
            results.extend([dict(FALLBACK)] * len(batch))

    return results


def classify_email(subject: str, sender: str, body: str) -> dict[str, Any]:
    """Single-email wrapper kept for backwards compatibility."""
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
        return parsed
    except Exception as e:
        logger.error(f"classify_email failed: {e}")
        return dict(FALLBACK)


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
