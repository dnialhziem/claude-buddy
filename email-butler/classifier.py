"""
classifier.py — Email classification using Ollama mistral:7b
Cleans email HTML, builds few-shot prompt, returns structured JSON score.
"""

import json
import logging
import re
import sys
import requests
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OLLAMA_URL: str = "http://localhost:11434/api/generate"
MODEL: str = "mistral:7b"
TIMEOUT: int = 90

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


def classify_email(subject: str, sender: str, body: str) -> dict[str, Any]:
    preview = clean_email(body)
    prompt = _build_prompt(subject, sender, preview)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0}
    }

    fallback = {
        "is_important": False,
        "score": 1,
        "category": "general",
        "reason": "Classification failed."
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        raw = response.json().get("response", "")

        match = re.search(r'\{.*\}', raw, re.DOTALL)
        parsed = json.loads(match.group()) if match else json.loads(raw)

        # Normalize: Ollama sometimes returns category as a list
        if isinstance(parsed.get("category"), list):
            parsed["category"] = parsed["category"][0] if parsed["category"] else "general"

        return parsed

    except requests.exceptions.ConnectionError:
        logger.error("Ollama connection refused. Verify service is running via: ollama serve")
        fallback["reason"] = "Ollama unavailable."
    except requests.exceptions.Timeout:
        logger.error(f"Ollama inference timed out after {TIMEOUT}s.")
        fallback["reason"] = "Inference timeout."
    except json.JSONDecodeError:
        logger.error("LLM generated invalid JSON structure.")
        fallback["reason"] = "JSON parsing failure."
    except Exception as e:
        logger.error(f"Unexpected classification error: {e}")
        fallback["reason"] = f"System error: {str(e)}"

    return fallback


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
