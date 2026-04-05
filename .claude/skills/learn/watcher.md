# Folder Watcher — Auto-Trigger /learn

Background script that monitors your Obsidian inbox and auto-runs the `/learn` pipeline when files are dropped in.

## Install Dependency

```bash
C:\Users\dnialhziem\AppData\Local\Python\bin\python.exe -m pip install watchdog
```

## Start the Watcher

```bash
C:\Users\dnialhziem\AppData\Local\Python\bin\python.exe scripts/learn-watcher.py
```

Leave this terminal open. It runs until you press `Ctrl+C`.

## How It Works

1. **You drop** a `.pdf`, `.pptx`, `.docx`, `.txt`, or folder into `obsidianvault\inbox\`
2. **Watcher detects** the new file (waits 5s for OneDrive sync to finish)
3. **Triggers** `claude -p "/learn <filepath>"` via CLI — runs the full learning pipeline
4. **Moves** the file to `inbox\processed\YYYY-MM-DD\` so it's not re-processed

## Inbox Folder Structure

```
obsidianvault\inbox\
  week3\              <- drop a folder for lecture pack mode
    lecture.pptx
    reading.pdf
  notes.pdf           <- drop a single file
  processed\          <- auto-moved here after processing
    2026-03-29\
      notes.pdf
```

## Run on Startup (Optional)

Create a `.bat` file in `shell:startup` (`Win+R` -> `shell:startup`):

```bat
@echo off
start /min "" "C:\Users\dnialhziem\AppData\Local\Python\bin\python.exe" "C:\Users\dnialhziem\OneDrive - The University of Melbourne\unimelb\year1\PYTHON-BUDDY\scripts\learn-watcher.py"
```

## Requirements

- `watchdog` Python package
- `claude` CLI on PATH (Claude Code installed)
- Obsidian vault at the expected OneDrive path

## Troubleshooting

- **"claude CLI not found"** — Install Claude Code CLI or add it to your PATH
- **Files not detected** — Make sure the watcher terminal is running; check `watcher.log`
- **Timeout** — Large files or slow NotebookLM responses may hit the 5-minute timeout. Run `/learn` manually for those.
- **OneDrive conflicts** — The 5s delay handles most sync lag. If files appear as 0 bytes, increase `time.sleep(5)` in the script

## Notes

- Only monitors the top level of `inbox\` (not recursive)
- Folders are treated as lecture packs — all supported files inside are extracted
- Unsupported file types are ignored silently
- All activity logged to `inbox\watcher.log`
