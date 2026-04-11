---
name: app-tracker
description: Use when someone asks to track an internship application, log a job application, update application status, list active applications, or check what they've applied for.
argument-hint: "add | update | list"
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Logs, updates, and lists internship applications in the Google Sheet `Applications` tab.

## Supporting Files

- [scripts/app_tracker.py](../../scripts/app_tracker.py) — main tracker script
- [scripts/shared/sheets.py](../../scripts/shared/sheets.py) — Google Sheets helper

## Prerequisites

```bash
pip install gspread google-auth
```

Environment variables required:
- `GOOGLE_CREDS_PATH` — path to your Google service account credentials.json
- `GOOGLE_SHEET_ID` — ID of your internship tracking Google Sheet

## Steps

1. Determine the subcommand from `$ARGUMENTS` or the user's request:
   - "add" / "log" / "track" → `add`
   - "update" / "change status" → `update`
   - "list" / "show" / "what have I applied to" → `list`

2. Run the script:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   python scripts/app_tracker.py $ARGUMENTS
   ```
   The script is interactive — it will prompt for details.

3. After `add`: suggest running `/cover-letter` or `/interview-prep` with the company name.
4. After `update` to Interview: suggest running `/interview-prep` for that company.
5. After `list`: if any deadlines are within 3 days, flag them to the user.

## Notes

- Valid statuses: `Applied`, `Interview`, `Offer`, `Rejected`, `Withdrawn`
- Application IDs are auto-generated (format: `APP-YYYYMMDD-HHMMSS`)
- `list` sorts by deadline ascending — closest deadlines first
- Rejected and Withdrawn applications are hidden from `list` output
