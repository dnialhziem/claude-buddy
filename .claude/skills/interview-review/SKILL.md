---
name: interview-review
description: Use when someone wants to practice interview answers, fill in interview prep, do a mock interview, answer prep questions, or review interview notes for a company.
argument-hint: "<company name>"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Opens your existing Obsidian interview prep note and walks you through each question
one at a time — you type your answer, it saves back to the note.

- Shows question + resume hints
- You type your answer (multi-line, press Enter twice to move on)
- Saves all answers back into the Obsidian note
- Ctrl+C stops early but saves progress so far

## Supporting Files

- [scripts/interview_review.py](../../../../career-toolkit/scripts/interview_review.py) — main script

## Prerequisites

Run `/interview-prep <company>` first to generate the note.

## Steps

1. Extract company name from `$ARGUMENTS`. If not provided, ask: "Which company do you want to review prep for?"

2. Run:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe scripts/interview_review.py $ARGUMENTS
   ```

3. The script runs interactively — user types answers directly in the terminal.

4. After completion, tell the user: "Answers saved to your Obsidian vault. Read them back out loud once before the interview."

## Notes

- Requires an existing prep note from `/interview-prep` — will error clearly if not found
- Answers are written back under each "My answer:" section in the note
- Ctrl+C mid-session saves progress — safe to stop and resume
- B = behavioral questions, T = technical questions
