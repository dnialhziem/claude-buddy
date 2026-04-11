# Claude Code — Python Buddy Project

This is the Python learning and skill-building workspace for Year 1.

---

## Purpose

This folder contains Claude Code skills used across all projects:
- `/python-buddy` — debug Python code with tiered solutions
- `/skill-builder` — create and audit new skills
- `/publish` — commit, push, sync vault skills, and keep GitHub clean after breakthroughs or new projects
- `/learn` — unified learning & research skill: brainstorm ideas, study files (PDF/PPTX/DOCX), research YouTube topics, or learn from URLs — all routes through YouTube search → NotebookLM → Obsidian vault with Mermaid mindmap
- `/delatex` — convert LaTeX/math notation into clean readable plain text (no symbols, no markup)
- `/butler` — run email briefing, sort inbox, audit classifications, or view receipt logs
- `/daily` — morning freelance briefing: fresh Airtasker gigs, job radar refresh, follow-ups due, upcoming deadlines
- `/interview-review` — walk through interview prep questions one by one, save your answers back to Obsidian

All session outputs are saved to the Obsidian vault at:
`C:\Users\<your-username>\OneDrive\Documents\Obsidian\obsidianvault\`

---

## Skills Location

```
.claude/skills/
  python-buddy/     — Python debugger (SKILL.md + error-catalogue.md + tier-guide.md)
  skill-builder/    — Skill creator and auditor (SKILL.md + reference.md)
  publish/          — GitHub publisher (SKILL.md)
  learn/            — Unified learning: brainstorm + YouTube + files + NotebookLM (SKILL.md + watcher.md)
  delatex/          — LaTeX to plain text converter (SKILL.md)
  butler/           — Email butler wrapper (SKILL.md)
  daily/            — Morning freelance briefing (SKILL.md)
```

---

## Python Setup

- Python 3.12: `C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\python.exe`
- Python 3.14: `C:\Users\<your-username>\AppData\Local\Python\bin\python.exe`
- Use **3.12** for notebooklm-py (3.14 has compatibility issues)
- Use **3.14** for everything else

---

## Session Efficiency

- After completing any major task (skill run, file saved, brainstorm wrapped up, resume compiled), suggest a `/compact` checkpoint to the user
- Say: "Good stopping point — want to `/compact` before starting the next task?"
- Do NOT suggest `/compact` mid-task or mid-skill — only at natural boundaries

---

## Student Context

- Year 1, University of Melbourne
- Developer path — AWS DVA-C02 target certification
- No ML background — use managed AI services (AWS, OpenAI API) not custom models
