---
name: cycle
description: Use when someone asks to run the full internship pipeline, process a job application end to end, or run the career cycle for a company.
argument-hint: "<company name or App ID>"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Runs the full internship application pipeline for one company in sequence:
1. Tailor resume to JD → push to GitHub
2. Generate cover letter
3. Generate interview prep Q&A + Anki flashcards
4. Draft follow-up email (queued for later)

## Steps

1. Extract company name or App ID from `$ARGUMENTS`. If not provided, ask: "Which company do you want to run the full cycle for?"

2. Confirm the plan with the user:
   ```
   Running full cycle for: [company]

   Steps:
   1. Tailor resume → update resume.html → push to GitHub
   2. Cover letter → save to CoverLetters tab
   3. Interview prep → save to PrepSheets tab + Anki flashcards
   4. Follow-up email → draft for later use

   Ollama must be running for Step 1.
   Anki must be open for Step 3.
   ```
   Ask: "Ready? (yes/no)"

3. **Step 1 — Tailor Resume:**
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe scripts/tailor_resume.py $ARGUMENTS --force
   ```
   Runs automatically with `--force` — no pause needed. Report outcome.

4. **Step 2 — Cover Letter:**
   ```bash
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe scripts/cover_letter.py $ARGUMENTS
   ```
   Report that draft is saved to CoverLetters tab.

5. **Step 3 — Interview Prep:**
   ```bash
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe scripts/interview_prep.py $ARGUMENTS
   ```
   Report Q&A generated and Obsidian note saved.

6. **Step 4 — Follow-Up (draft only):**
   ```bash
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe scripts/follow_up.py $ARGUMENTS
   ```
   If too early (< 5 days since applying), note it and skip — don't treat as error.

7. Print a completion summary:
   ```
   ── Cycle Complete: [company] ──

   Resume:       Updated + pushed to GitHub (PDF compiling)
   Cover Letter: Saved to CoverLetters tab
   Interview:    Obsidian note saved to vault
   Follow-up:    Drafted (send in X days)

   Next: /app-tracker update [company] when you hear back.
   ```

## Notes

- Run steps sequentially — each depends on the application existing in the Sheet
- If any step fails, report the error and continue to the next step (don't abort the whole cycle)
- tailor-resume is interactive — it will pause and ask for approval before modifying files
- follow-up will exit early if < 5 days since applying — this is expected behaviour, not an error
- The cycle does NOT submit applications — that's always manual
