---
name: tailor-resume
description: Use when someone asks to tailor their resume for a job, update resume for an application, customise resume to match a job description, or optimise resume for ATS.
argument-hint: "<company name or App ID>"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Pulls the JD from the Radar tab, sends resume + JD to Ollama, shows suggested profile rewrite + bullet rewrites. On approval, updates resume/resume.html and pushes to GitHub to trigger PDF compilation via GitHub Actions.

## Supporting Files

- [scripts/tailor_resume.py](../../scripts/tailor_resume.py) — main tailoring script
- [scripts/shared/sheets.py](../../scripts/shared/sheets.py) — Google Sheets helper
- [scripts/shared/jd_fetch.py](../../scripts/shared/jd_fetch.py) — JD fetcher

## Prerequisites

Ollama must be running:
```bash
ollama serve
```
Model used: `mistral:7b` (already pulled)

## Steps

1. Extract company name or App ID from `$ARGUMENTS`. If not provided, ask: "Which company or App ID do you want to tailor the resume for?"

2. Run the script:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   python scripts/tailor_resume.py $ARGUMENTS
   ```

3. The script will:
   - Look up the application in the Sheet
   - Fetch the JD from the job URL
   - Send resume + JD to Ollama (mistral:7b)
   - Display: profile rewrite, bullet rewrites, skills to add, top ATS keywords
   - Ask the user to approve (1) or skip (2)
   - If approved: update resume/resume.html → git commit → git push → GitHub Actions compiles PDF

4. After push, remind the user: "GitHub Actions will compile the updated PDF in ~60 seconds. Check the Releases page."

5. Suggest next step: "Run `/cover-letter $ARGUMENTS` to generate a cover letter using the updated resume."

## Notes

- Ollama must be running — script exits clearly if not
- Only the profile section is auto-applied; bullet rewrites are shown for manual editing
- Every push triggers the full CI/CD pipeline (ATS PDF + visual PDF + LinkedIn draft)
- Application must exist in `Applications` tab first
