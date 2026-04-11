---
name: cover-letter
description: Use when someone asks to write a cover letter, draft a cover letter, generate a cover letter for a job, or tailor a cover letter for an internship application.
argument-hint: "<company name or App ID>"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Pulls an application from the Google Sheet, fetches the full JD via Playwright, and generates a tailored cover letter using Groq AI (Ollama fallback). Saves the draft to the `CoverLetters` tab.

## Supporting Files

- [scripts/cover_letter.py](../../scripts/cover_letter.py) — main generation script
- [scripts/shared/sheets.py](../../scripts/shared/sheets.py) — Google Sheets helper
- [scripts/shared/jd_fetch.py](../../scripts/shared/jd_fetch.py) — JD fetcher

## Prerequisites

```bash
pip install groq gspread google-auth playwright
playwright install chromium
```

Environment variables required:
- `GROQ_API_KEY` — Groq API key
- `GOOGLE_CREDS_PATH` — path to Google service account credentials.json
- `GOOGLE_SHEET_ID` — Google Sheet ID

## Steps

1. Extract the company name or App ID from `$ARGUMENTS`. If not provided, ask: "Which company or App ID do you want to generate a cover letter for?"

2. Run the script:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   python scripts/cover_letter.py $ARGUMENTS
   ```

3. The script will:
   - Look up the application in the Sheet
   - Fetch the JD from the job URL
   - Generate using Groq (falls back to Ollama if Groq fails)
   - Print the letter and save it to the CoverLetters tab

4. After output, ask: "Want me to refine any section — tone, opening, or specific project highlight?"

## Notes

- Application must exist in the `Applications` tab first — run `/app-tracker add` if not
- If Groq API key is missing or quota exceeded, script falls back to Ollama (mistral:7b must be running)
- Letter is capped at 400 words — intentional, recruiters don't read longer ones
- Never invents experience — only uses what's in resume/resume.html
