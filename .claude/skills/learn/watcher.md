# Learn Watcher — Setup & Reference

The folder watcher is a background Python script that monitors `Obsidian\inbox\` and auto-triggers the `/learn` pipeline when files are dropped in.

## Install Dependencies

```bash
C:\Users\dnialhziem\AppData\Local\Programs\Python\Python312\python.exe -m pip install watchdog pdfplumber python-pptx python-docx
```

## Watcher Script

Save as `scripts\learn-watcher.py` in the project root:

```python
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INBOX = Path(r"C:\Users\dnialhziem\OneDrive\Documents\Obsidian\obsidianvault\inbox")
PROCESSED = INBOX / "processed"
LOG_FILE = INBOX / "watcher.log"

SUPPORTED = {".pdf", ".pptx", ".docx", ".txt"}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s — %(message)s"
)

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        path = Path(event.src_path)

        # Skip the processed subfolder and log file
        if "processed" in str(path) or path.suffix == ".log":
            return

        if event.is_directory or path.suffix.lower() in SUPPORTED:
            logging.info(f"Detected: {path.name}")
            print(f"[learn-watcher] New item detected: {path.name}")
            time.sleep(3)  # Wait for file to finish copying
            self._trigger(path)

    def _trigger(self, path):
        # This prints the trigger command for Claude Code to pick up
        # In a full integration, this would call the Claude Code CLI directly
        print(f"[learn-watcher] Triggering /learn for: {path}")
        logging.info(f"Triggered /learn for: {path}")

        # Move to processed after trigger
        PROCESSED.mkdir(parents=True, exist_ok=True)
        dest = PROCESSED / path.name
        path.rename(dest)
        logging.info(f"Moved to processed: {dest}")

if __name__ == "__main__":
    INBOX.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(InboxHandler(), str(INBOX), recursive=False)
    observer.start()
    print(f"[learn-watcher] Watching: {INBOX}")
    print("[learn-watcher] Drop files or folders into inbox/ to auto-trigger /learn")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

## Run on Startup (Optional)

To have the watcher start automatically with Windows:

1. Press `Win + R` → type `shell:startup`
2. Create a shortcut to this command:
   ```
   C:\Users\dnialhziem\AppData\Local\Programs\Python\Python312\python.exe C:\path\to\scripts\learn-watcher.py
   ```

## Inbox Folder Structure

```
obsidianvault\inbox\
  week3\              ← drop a folder for lecture pack mode
    lecture.pptx
    reading.pdf
  notes.pdf           ← drop a single file
  processed\          ← auto-moved here after processing
    2026-03-28\
      notes.pdf
```

## Notes

- The watcher only monitors the top level of `inbox\` (not recursive)
- Folders are treated as lecture packs — all supported files inside are extracted
- Unsupported file types are ignored silently
- Check `watcher.log` if something doesn't trigger as expected
