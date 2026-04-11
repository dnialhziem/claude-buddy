---
name: daily
description: Use when someone asks to run the daily briefing, check freelance gigs, morning update, what's due today, or daily summary.
argument-hint: ""
disable-model-invocation: true
allowed-tools: Bash, Read
---

## What This Skill Does

Runs the morning freelance briefing in one command:
1. Airtasker — scrapes fresh gigs (IT, data entry, writing)
2. Job Radar — refreshes Freelance tab via SearXNG
3. Follow-ups — flags applications 5+ days old with no response
4. Deadlines — shows applications due in the next 7 days

## Supporting Files

- [scripts/daily.py](../../../../career-toolkit/scripts/daily.py) — main orchestrator
- [scripts/airtasker_radar.py](../../../../career-toolkit/scripts/airtasker_radar.py) — Airtasker scraper
- [scripts/job_radar.py](../../../../career-toolkit/scripts/job_radar.py) — SearXNG job search

## Prerequisites

```bash
pip install playwright gspread google-auth requests
playwright install chromium
```

SearXNG must be running:
```bash
cd C:/Users/dnialhziem/AI-Stack/setup && docker-compose up -d searxng
```

## Steps

1. Check SearXNG is running. If not, tell user to start Docker first.

2. Run:
   ```bash
   cd c:/Users/dnialhziem/career-toolkit
   C:/Users/dnialhziem/AppData/Local/Python/bin/python.exe scripts/daily.py
   ```

3. Report the output:
   - How many Airtasker gigs were added
   - How many freelance listings refreshed
   - Any follow-ups due (flag these explicitly)
   - Any deadlines in next 7 days (flag URGENT if ≤ 2 days)

## Notes

- Focused on freelance only — not a full internship pipeline
- Airtasker requires Playwright + Chromium
- SearXNG must be running for job radar step
- Follow-up threshold is 5 days after Date Applied
- Deadlines within 2 days are flagged as URGENT
