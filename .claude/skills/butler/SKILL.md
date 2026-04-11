---
name: butler
description: Use when someone asks to check emails, run email briefing, sort inbox, audit email classifications, or view receipt logs.
argument-hint: "briefing | sort | audit | receipts"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Runs the email butler CLI — morning briefing, inbox sorting, accuracy audit, or receipt log. Ollama classifies emails locally; no paid API required.

## Supporting Files

- [email-butler/butler.py](../../../../email-butler/butler.py) — main CLI entrypoint
- [email-butler/classifier.py](../../../../email-butler/classifier.py) — Ollama-based email classifier with pre-filter rules
- [email-butler/gmail.py](../../../../email-butler/gmail.py) — Gmail API fetch + label management

## Prerequisites

```bash
pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client
```

Ollama must be running: `ollama serve`

## Steps

1. Determine subcommand from `$ARGUMENTS` or user's request:
   - "briefing" / "check emails" / "morning briefing" → `briefing`
   - "sort" / "sort inbox" / "move emails" → `sort`
   - "audit" / "accuracy report" → `audit`
   - "receipts" / "show orders" → `receipts`
   - If no argument, default to `briefing`

2. Run the butler:
   ```bash
   cd "C:/Users/dnialhziem/OneDrive - The University of Melbourne/unimelb/year1/PYTHON-BUDDY/email-butler"
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe butler.py $ARGUMENTS
   ```

3. Report the output to the user.

4. After `briefing`: if any HIGH priority emails appear, flag them explicitly.
5. After `sort`: confirm how many emails were moved and to which labels.

## Notes

- Ollama must be running for classification — start with `ollama serve` if emails time out
- `briefing` pre-filters obvious junk instantly, then classifies remainder in parallel (3 workers)
- `sort` moves emails into Gmail labels under `Butler/` — never deletes anything
- `audit` shows classification accuracy based on any corrections you've logged
- `receipts` shows all logged order/receipt emails
- If a HIGH email is misclassified as LOW, correct it: `butler.py correct --email-id ID --correct-label HIGH`
