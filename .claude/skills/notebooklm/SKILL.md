---
name: notebooklm
description: Use when sending sources to NotebookLM for analysis, creating a notebook, adding YouTube URLs or text, or generating deliverables like summaries, study guides, mind maps, or infographics.
argument-hint: [source URL or topic]
disable-model-invocation: true
---

## What This Skill Does

Controls NotebookLM via CLI to create notebooks, add sources (YouTube URLs, text, files), run analysis, and generate deliverables. Used as a sub-skill by youtube-pipeline but can be called directly.

## Python Executable

Always use: `C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\python.exe`
Base command: `C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\python.exe -m notebooklm`

## Available Commands

```bash
# List existing notebooks
python -m notebooklm list

# Create a new notebook
python -m notebooklm create --title "Title Here"

# Add a YouTube URL as source
python -m notebooklm add-source NOTEBOOK_ID --url "https://youtube.com/..."

# Add text directly as source
python -m notebooklm add-source NOTEBOOK_ID --text "text content here"

# Chat / ask a question about the notebook
python -m notebooklm chat NOTEBOOK_ID "Your question here"

# Generate a study guide
python -m notebooklm study-guide NOTEBOOK_ID

# Generate an audio overview (podcast)
python -m notebooklm audio-overview NOTEBOOK_ID

# List available note types
python -m notebooklm --help
```

## Execution Flow

### Step 1: Create a Notebook

```bash
C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\python.exe -m notebooklm create --title "[topic]-[date]"
```

Note the notebook ID returned.

### Step 2: Add Sources

For each YouTube URL provided:
```bash
C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\python.exe -m notebooklm add-source NOTEBOOK_ID --url "URL"
```

Wait for each source to be processed before adding the next.

### Step 3: Run Analysis

Ask the notebook a specific analysis question:
```bash
C:\Users\<your-username>\AppData\Local\Programs\Python\Python312\python.exe -m notebooklm chat NOTEBOOK_ID "ANALYSIS_QUESTION"
```

### Step 4: Generate Deliverable (if requested)

If the user asked for a specific deliverable:
- Study guide: `python -m notebooklm study-guide NOTEBOOK_ID`
- Audio overview: `python -m notebooklm audio-overview NOTEBOOK_ID`
- For other deliverable types, use the chat command with a specific request

### Step 5: Save Output to Vault

Save all analysis output to:
`C:\Users\<your-username>\OneDrive\Documents\Obsidian\obsidianvault\videos\[topic-slug]-[date].md`

Use this template:
```markdown
# NotebookLM Analysis: [Topic]
**Date:** [YYYY-MM-DD]
**Sources:** [list of URLs]
**Notebook ID:** [id]

## Analysis
[output from chat/analysis]

## Deliverable
[output from study guide, audio overview, etc. if requested]

## Key Takeaways
[3-5 bullet points]
```

## Notes

- NotebookLM supports up to 50 sources per notebook
- Audio overviews and slide decks can take 5–15 minutes to generate
- If not logged in, run: `python -m notebooklm login` (use Python 3.12)
- All outputs must be saved to the vault — never leave analysis only in the terminal
