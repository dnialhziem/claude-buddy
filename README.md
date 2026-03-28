# Claude Buddy — AI Environment Explorer

A living workspace for understanding how AI developer tools actually work — not just using them, but building with them, breaking them, and figuring out why.

This isn't a finished product. It's an ongoing exploration of the AI tooling ecosystem: how language models, automation pipelines, and knowledge systems can be wired together into something genuinely useful for a developer.

---

## Why I Built This

Most people consume AI tools. I wanted to understand them from the inside.

This project is how I do that — by building real workflows from scratch, debugging what breaks, and documenting what I learn along the way. Every skill added, every pipeline tested, every fix committed is a step toward actually understanding how these systems work rather than just prompting my way through them.

---

## What It Does

```
YouTube → yt-dlp → NotebookLM → Obsidian vault → Claude context → repeat
```

Each skill is a modular command. Run one, or chain them into a pipeline.

| Skill | Command | What it does |
|-------|---------|-------------|
| YouTube Search | `/youtube-search` | Searches YouTube via yt-dlp, returns top 10 results with metadata |
| NotebookLM | `/notebooklm` | Controls NotebookLM — creates notebooks, adds sources, runs analysis |
| YouTube Pipeline | `/youtube-pipeline` | Full pipeline: search → NotebookLM → analysis → saved to vault |
| Python Buddy | `/python-buddy` | Debugs Python code with tiered solutions (easy/moderate/advanced) |
| Brainstorm | `/brainstorm` | Interactive idea sessions, saved to vault for future reference |
| Skill Builder | `/skill-builder` | Creates and audits new skills |

---

## Architecture

```
PYTHON-BUDDY/
├── .claude/
│   └── skills/
│       ├── youtube-search/     # yt-dlp wrapper
│       ├── notebooklm/         # NotebookLM CLI controller
│       ├── youtube-pipeline/   # Search + analysis super-skill
│       ├── python-buddy/       # Python debugger with error catalogue
│       ├── brainstorm/         # Idea generation sessions
│       └── skill-builder/      # Skill creator and auditor
├── CLAUDE.md                   # Project instructions loaded by Claude Code
└── launch-claude.bat           # Opens Claude Code with vault context attached
```

Session outputs, research notes, and brainstorm summaries are saved to a separate Obsidian vault (not in this repo — personal knowledge base).

---

## Stack

- **Claude Code** — AI CLI that loads and executes skills
- **yt-dlp** — YouTube metadata extraction (no downloads)
- **notebooklm-py** — Unofficial Python CLI for NotebookLM via Playwright
- **Obsidian** — Markdown-based knowledge base (vault)
- **Python 3.12** — Runtime for notebooklm-py (3.14 has compatibility issues)

---

## Setup

### Prerequisites
- [Claude Code](https://claude.ai/code) installed
- Python 3.12: `winget install Python.Python.3.12`
- yt-dlp: `pip install yt-dlp`
- notebooklm-py: `pip install notebooklm-py && python -m playwright install chromium`

### Install
```bash
git clone https://github.com/<your-username>/claude-buddy.git
cd claude-buddy
```

### Authenticate NotebookLM
```bash
C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe -m notebooklm login
```

### Run
Open Claude Code from this directory:
```bash
claude --add-dir "path/to/your/obsidian/vault"
```

Then invoke any skill:
```
/youtube-pipeline euclidean vectors in R3
/python-buddy
/brainstorm
```

---

## Example Output

Running `/youtube-pipeline euclidean vectors in R3` on 3 YouTube videos produced:

- Key concepts: 2D→3D transition, vector mechanics, spatial geometry
- CS applications: game engine projection, physics simulations, multi-dimensional arrays
- Saved to vault: `videos/euclidean-vectors-r3-2026-03-27.md`

---

## What I Learned Building This

- Claude Code's skill system uses `SKILL.md` files loaded from `.claude/skills/` — each skill is a markdown prompt with frontmatter
- `disable-model-invocation: true` prevents expensive skills from auto-triggering
- notebooklm-py requires Python 3.12 specifically — 3.14 breaks Playwright's browser automation
- The `--add-dir` flag lets Claude Code load context from multiple project directories simultaneously
- `notebooklm source add --type youtube` is the correct flag — took debugging to find this

---

## Roadmap

- [ ] Refactor into a proper Python CLI (`buddy search`, `buddy pipeline`)
- [ ] Add test suite for each skill
- [ ] AWS skill — research pipeline for DVA-C02 certification prep
- [ ] Auto-generate Obsidian graph links between related research sessions

---

*Year 1, University of Melbourne — Developer track | Exploring AI tooling from the ground up*
