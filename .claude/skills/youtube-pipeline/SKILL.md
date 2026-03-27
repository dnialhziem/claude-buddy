---
name: youtube-pipeline
description: Use when someone wants to research a topic using YouTube videos, analyze video content with NotebookLM, or get a deliverable (summary, study guide, mind map) from YouTube research.
argument-hint: [topic] [optional: deliverable type]
disable-model-invocation: true
---

## Credit

Inspired by [Chase AI](https://www.youtube.com/@ChaseAI) — his Claude Code + NotebookLM pipeline workflow introduced this concept.

---

## What This Skill Does

Full YouTube research pipeline. Searches YouTube for videos on a topic, sends them to NotebookLM for AI analysis, returns structured insights, and saves everything to the Obsidian vault.

Combines the `youtube-search` and `notebooklm` skills into one command.

## Python Executable

Always use: `C:\Users\dnialhziem\AppData\Local\Programs\Python\Python312\python.exe`

## Inputs

- `$ARGUMENTS` — the research topic + optional deliverable type
- Examples:
  - `/youtube-pipeline Python AWS tutorial`
  - `/youtube-pipeline Claude Code MCP servers — infographic`
  - `/youtube-pipeline FastAPI beginner — study guide`

## Execution Flow

### Step 1: Parse the Request

Extract from `$ARGUMENTS`:
- **Topic** — what to search for
- **Deliverable** — optional (study guide, audio overview, summary, infographic). Default: summary only.

If no arguments provided, ask:
1. "What topic do you want to research on YouTube?"
2. "What deliverable do you want? (summary / study guide / audio overview / none)"

### Step 2: YouTube Search

Use the `youtube-search` skill to find the top 5–10 videos for the topic.

Present the results to the user and ask:
"Here are the top results. Should I send all of them to NotebookLM, or do you want to pick specific ones?"

Wait for confirmation before proceeding.

### Step 3: Create NotebookLM Notebook

Use the `notebooklm` skill to:
1. Create a new notebook titled: `[topic]-[YYYY-MM-DD]`
2. Add each selected YouTube URL as a source
3. Wait for all sources to process

### Step 4: Run Analysis

Ask NotebookLM this analysis question (adapt based on topic):
```
Analyse these videos on [topic]. Provide:
1. Key concepts and themes across all videos
2. Points of agreement between creators
3. Gaps or contradictions
4. The most important things to remember
5. How this applies to a Year 1 CS student learning [topic]
```

### Step 5: Generate Deliverable

If a deliverable was requested, generate it using the `notebooklm` skill.

Inform the user:
- Summary/study guide: ready in ~2 minutes
- Audio overview: ready in ~5–10 minutes
- Infographic/slides: ready in ~10–15 minutes

### Step 6: Save to Vault

Save the full output to:
`C:\Users\dnialhziem\OneDrive\Documents\Obsidian\obsidianvault\videos\[topic-slug]-[date].md`

Include: sources used, full analysis, deliverable output, key takeaways.

Tell the user: "Saved to your Obsidian vault at videos/[filename]"

### Step 7: Update CLAUDE.md (Optional)

If the user asks for it or if this was a particularly rich research session, suggest:
"Want me to update your vault CLAUDE.md to reflect any new preferences from this session?"

## Notes

- `disable-model-invocation: true` is set — always invoke with `/youtube-pipeline`, never auto-triggered
- This is the most expensive skill in the workflow — confirm with user before running
- Always save to vault — the whole point is the knowledge accumulates over time
- If NotebookLM is not authenticated, stop and tell user to run: `python -m notebooklm login`
