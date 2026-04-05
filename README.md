# Claude Buddy — AI Developer Toolkit

A living workspace for building real AI-powered workflows from scratch — not just prompting, but wiring language models, automation pipelines, and knowledge systems into tools that actually do something.

This project grows alongside my developer journey. Every skill added, every pipeline debugged, every commit is a step toward understanding how these systems work from the inside.

---

## Why I Built This

Most people use AI tools. I wanted to build with them.

This repo is how I do that — by creating modular Claude Code skills, automating real workflows (file sorting, learning pipelines, publishing), and connecting AI to the tools I already use (Obsidian, n8n, Google Sheets). The goal isn't to finish it — it's to keep building.

---

## Skills

Each skill is a modular command invoked inside Claude Code.

| Command | What it does |
|---------|-------------|
| `/python-buddy` | Debugs Python errors with tiered solutions (easy → advanced). Includes an error catalogue and tier guide. |
| `/learn` | Unified learning pipeline: study PDFs/PPTX/DOCX, research YouTube topics, or brainstorm ideas — all saved to Obsidian vault with a Mermaid mindmap |
| `/publish` | Commits, pushes, and keeps the GitHub repo clean after a breakthrough. Scans for sensitive info before staging. |
| `/skill-builder` | Creates and audits new Claude Code skills from scratch |
| `/delatex` | Converts LaTeX and math notation into clean readable plain text — no symbols, no markup |

---

## Projects

### File Sorter Agent
*Personal — 2026*

Watchdog-based agent that monitors a folder and uses a local LLM (Ollama) to classify and move files automatically. After sorting, it sends a webhook to n8n which logs the event (filename, destination, timestamp) to Google Sheets in real time.

**Stack:** Python 3.14, Watchdog, Ollama, n8n, Google Sheets API
**File:** [`file-sorter-agent.py`](file-sorter-agent.py)

---

## Architecture

```
claude-buddy/
├── .claude/
│   └── skills/
│       ├── python-buddy/       # Python debugger (SKILL.md + error-catalogue + tier-guide)
│       ├── learn/              # Unified learning pipeline (SKILL.md + watcher.md)
│       ├── publish/            # GitHub publisher (SKILL.md)
│       ├── skill-builder/      # Skill creator and auditor (SKILL.md + reference.md)
│       └── delatex/            # LaTeX to plain text converter (SKILL.md)
├── file-sorter-agent.py        # Watchdog + Ollama + n8n file automation agent
├── CLAUDE.md                   # Project instructions loaded by Claude Code
└── launch-claude.bat           # Opens Claude Code with Obsidian vault context
```

Session outputs and research notes are saved to a private Obsidian vault (not in this repo).

---

## Stack

- **Claude Code** — AI CLI that loads and executes skills from `.claude/skills/`
- **Ollama** — Local LLM runtime used by the file sorter for classification
- **Watchdog** — Python library for monitoring filesystem events
- **n8n** — Visual workflow automation (webhook trigger → Google Sheets logging)
- **Obsidian** — Markdown knowledge base where all session outputs are saved
- **Python 3.14** — Primary runtime

---

## Setup

### Prerequisites
- [Claude Code](https://claude.ai/code) installed
- Python 3.14: `winget install Python.Python.3.14`
- Ollama: [ollama.com](https://ollama.com) — pull any model (`ollama pull llama3`)

### Install
```bash
git clone https://github.com/dnialhziem/claude-buddy.git
cd claude-buddy
pip install watchdog requests
```

### Run File Sorter Agent
```bash
python file-sorter-agent.py
```

### Run Claude Code with Obsidian vault
```bash
claude --add-dir "path/to/your/obsidian/vault"
```

Then invoke any skill:
```
/python-buddy
/learn euclidean vectors
/delatex
/publish
```

---

## What I Learned Building This

- Claude Code skills use `SKILL.md` files in `.claude/skills/` — each is a markdown prompt with YAML frontmatter controlling when and how it triggers
- `disable-model-invocation: true` prevents expensive skills from auto-triggering on every message
- n8n's webhook test URL only works when actively listening in the UI — the production URL is always on
- Watchdog's `on_created` fires before a file write completes — added a short sleep to avoid reading partial files
- Pylint's `W0718` (broad-exception-caught) is worth fixing — catching `requests.RequestException` instead of bare `Exception` makes failures easier to trace

---

## Roadmap

- [ ] AWS research skill — learning pipeline for DVA-C02 certification prep
- [ ] File sorter: add confidence threshold so low-confidence files go to an "unsorted" review folder
- [ ] Skill usage dashboard — track which skills are invoked most across sessions

---

*Year 1, University of Melbourne — Developer track | AWS DVA-C02 target*
