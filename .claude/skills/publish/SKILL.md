---
name: publish
description: Use when the user wants to commit, push, update GitHub, publish a new project, ship a skill update, or sync the repo after a breakthrough or milestone.
argument-hint: "optional: what changed or project name"
disable-model-invocation: true
---

## What This Skill Does

One command to commit, push, and keep the GitHub repo clean and readable after a breakthrough, new project, or skill update. Writes commit messages and README updates that a non-technical reader (e.g. HR recruiter) can understand at a glance.

Repo: `https://github.com/dnialhziem/claude-buddy`

---

## Step 1: Show Repo Status

Run:
```bash
git status
git diff --stat
```

If the output shows "nothing to commit, working tree clean" — tell the user: "Nothing to publish — your repo is already up to date." Then stop.

Otherwise, present a plain-English summary of what's changed:
- New files added
- Files modified
- Files deleted
- Anything untracked that might need to be included

Ask the user: "Is this everything you want to publish, or are there other files to include?"

---

## Step 2: Sensitive Info Scan

Before anything is staged, scan all changed and untracked files for content that should NOT be on a public GitHub repo:

**Flag immediately if found:**
- API keys, tokens, passwords, or secrets (look for patterns like `sk-`, `Bearer `, `API_KEY=`, `password=`, `token=`)
- Personal details: full name + student ID together, home address, phone number, bank/payment info
- University login credentials or student portal URLs with embedded session tokens
- Hardcoded file paths that reveal personal folder structure (e.g. `C:\Users\dnialhziem\...`) inside code files — note: this is fine in SKILL.md documentation, but not in Python scripts or config files
- `.env` files or any file named `secrets`, `credentials`, `config.local`

**If sensitive info is detected, stop and report:**
```
STOP — Sensitive information detected before publishing:

File: [filename]
Line: [line number]
Issue: [what was found — e.g. "API key pattern detected"]
Risk: [what happens if this is published publicly]

Options:
1. Remove or mask the sensitive info, then re-run /publish
2. Add the file to .gitignore so it's never tracked
3. Skip this file from the current commit
```

Do NOT proceed until the user resolves all flagged issues.

If nothing is found, continue to Step 3.

---

## Step 3: Downgrade Check

Before proceeding, scan for any changes that could reduce the repo's quality:
- Deleted or shortened README sections
- Removed skill files
- Removed supporting files (error-catalogue, tier-guide, etc.)
- Any file deletion

If found, **stop and present a pros/cons table** before continuing:

```
## Before I remove/change [X], here's what that means:

| | Detail |
|---|---|
| **What's changing** | [describe exactly what would be removed or reduced] |
| **Pro** | [reason it might be a good idea] |
| **Con** | [what the repo or profile loses] |
| **Recruiter impact** | [how this looks to someone reading the repo] |

Do you want to proceed with this change, skip it, or keep the original?
```

Wait for the user's decision before moving forward.

---

## Step 4: Sync Skills to Vault

Copy updated skill files from PYTHON-BUDDY to the Obsidian vault:

```bash
cp -r "C:/Users/dnialhziem/OneDrive - The University of Melbourne/unimelb/year1/PYTHON-BUDDY/.claude/skills/." \
      "C:/Users/dnialhziem/OneDrive/Documents/Obsidian/obsidianvault/.claude/skills/"
```

Tell the user: "Skills synced to vault." (This is always safe — vault skills are copies, not originals.)

---

## Step 5: Check for New Projects

Ask the user directly: "Are you publishing a new project alongside this update? (class assignment, hackathon, personal project)"

If yes, ask:
1. "What is this project? (one sentence — what it does and why you built it)"
2. "Is this a class project, hackathon, or personal project?"
3. "What tools or languages did you use?"

Use the answers to add a new entry to the README under a `## Projects` section (create it if it doesn't exist yet).

If no, skip this step.

**Project entry format:**
```markdown
### [Project Name]
*[Class / Hackathon / Personal] — [Year]*

[One sentence: what it does and why it exists]

**Stack:** [languages/tools used]
**Repo:** [link if separate, or "part of this repo"]
```

---

## Step 6: Draft the Commit Message

Write a commit message in two parts:

**Title line** (50 chars max):
- Start with a type: `feat:`, `fix:`, `docs:`, `skill:`
- Plain English — a recruiter should understand it
- Examples:
  - `feat: add github publish skill`
  - `skill: update python-buddy with error catalogue`
  - `docs: add COMP10001 project to README`
  - `fix: correct notebooklm source add command`

**Body** (optional, for big milestones):
- 2–3 sentences explaining what changed and why
- Written like a short professional update, not code jargon

Show the draft to the user and ask: "Does this commit message look right?"

---

## Step 7: Commit and Push

Once the user confirms the message:

```bash
git add .
git commit -m "[confirmed message]"
git push
```

---

## Step 8: Confirm

Tell the user:
```
Published. View your repo at:
https://github.com/dnialhziem/claude-buddy
```

If the README was updated, mention which section changed.
If skills were synced, confirm that too.

---

## Notes

- **Never push without showing what's being committed first** — always show git status summary in Step 1
- **Never silently downgrade** — any removal or reduction triggers Step 2 pros/cons check
- **Vault sync is always safe** — vault skills are copies, originals live in PYTHON-BUDDY. Auto-sync is fine.
- **Commit messages are for humans** — avoid jargon, write as if explaining to a recruiter
- If `$ARGUMENTS` is provided, use it as context for the commit message draft
- If the user is unsure what changed, run `git diff` and summarize it for them
