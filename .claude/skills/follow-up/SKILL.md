---
name: follow-up
description: Use when someone asks to write a follow-up email, send a follow-up after applying, draft a thank-you email after an interview, or check in on an application status.
argument-hint: "<company name or App ID>"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Detects whether a follow-up or thank-you email is appropriate based on application status and days elapsed, then generates the correct email using Groq (Ollama fallback).

- **Applied + 5+ days ago** → follow-up email (checking status)
- **Status = Interview** → thank-you email (post-interview)
- **Applied + < 5 days** → tells user it's too early

## Supporting Files

- [scripts/follow_up.py](../../scripts/follow_up.py) — main email generation script
- [scripts/shared/sheets.py](../../scripts/shared/sheets.py) — Google Sheets helper

## Prerequisites

```bash
pip install groq gspread google-auth
```

Environment variables required:
- `GROQ_API_KEY`
- `GOOGLE_CREDS_PATH`
- `GOOGLE_SHEET_ID`

## Steps

1. Extract company name or App ID from `$ARGUMENTS`. If not provided, ask: "Which company or App ID do you want to follow up on?"

2. Run the script:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   python scripts/follow_up.py $ARGUMENTS
   ```

3. The script auto-detects email type and prints:
   - Subject line
   - Email body (ready to copy-paste)

4. Remind the user: "Always read and personalise before sending — especially fill in [topic discussed] in thank-you emails."

5. After a thank-you email: suggest running `/app-tracker update` to log the interview status.

## Notes

- Follow-up threshold is 5 days — script exits cleanly if too early
- Email is printed only — never sent automatically
- Groq falls back to Ollama (mistral:7b) if API key missing or quota exceeded
- Resume context is hardcoded as a short snippet — update `resume_snippet` in the script if profile changes significantly
