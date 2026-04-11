---
name: interview-prep
description: Use when someone asks to prepare for an interview, generate interview questions, create interview prep, practice interview answers, or get ready for a job interview.
argument-hint: "<company name or App ID>"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Pulls an application from the Sheet, fetches the JD, generates 3 behavioral + 3 technical questions with resume-grounded talking point hints. Saves to `PrepSheets` tab and writes a structured Obsidian note with questions, hints, technical terms glossary, questions to ask the interviewer, and after-interview checklist.

## Supporting Files

- [scripts/interview_prep.py](../../scripts/interview_prep.py) — main generation script
- [scripts/shared/sheets.py](../../scripts/shared/sheets.py) — Google Sheets helper
- [scripts/shared/jd_fetch.py](../../scripts/shared/jd_fetch.py) — JD fetcher

## Prerequisites

```bash
pip install gspread google-auth playwright
playwright install chromium
```

Environment variables required:
- `GOOGLE_CREDS_PATH`
- `GOOGLE_SHEET_ID`

## Steps

1. Extract the company name or App ID from `$ARGUMENTS`. If not provided, ask: "Which company or App ID do you want to prep for?"

2. Run the script:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   python scripts/interview_prep.py $ARGUMENTS
   ```

3. The script will:
   - Look up application in Sheet
   - Fetch JD from job URL
   - Generate 3 behavioral + 3 technical questions with resume-grounded hints via Ollama
   - Save to `PrepSheets` tab
   - Write Obsidian note to `obsidianvault/projects/interview-prep/<Company>-<date>.md`

4. After output, tell the user: "Note saved to your Obsidian vault. Fill in the 'My answer' sections in your own words before the interview."

## Notes

- Uses Ollama (mistral:7b) — no paid API required
- Hints are grounded in resume/resume.html — never invents experience
- Note includes: "Tell me about yourself" scaffold, STAR answer prompts, technical terms glossary, questions to ask interviewer, after-interview follow-up reminder
- Application must exist in `Applications` tab — run `/app-tracker add` first
- Questions are calibrated for Year 1/2 internship interviews, not senior roles
