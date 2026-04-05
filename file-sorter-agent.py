"""File sorter agent: watches the year1 folder and auto-sorts new files into subject subfolders."""

import os
import shutil
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── CONFIG ──────────────────────────────────────────────────────────────────
WATCH_FOLDER = r"C:\Users\dnialhziem\OneDrive - The University of Melbourne\unimelb\year1"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral:7b"

# Folders to never move files into
SKIP_FOLDERS = {"PYTHON-BUDDY"}

# Temp/incomplete download extensions to ignore
IGNORE_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}

# Subject keywords for keyword classifier
SUBJECT_KEYWORDS = {
    "blaw":            ["law", "blaw", "contract", "legal", "case"],
    "comp 10001":      ["comp", "computing", "algorithm", "code"],
    "linearalgebra":   ["linear", "matrix", "mast", "algebra", "vector", "eigen"],
    "python learning": ["python", "exercise", "practice"],
    "tstw":            ["science", "scie", "tstw", "biology"],
}


N8N_WEBHOOK_URL = "https://dnialhziem.app.n8n.cloud/webhook/file-sorter"


def notify_n8n(filename: str, destination: str):
    """Send a log entry to n8n after a file is moved."""
    try:
        requests.post(N8N_WEBHOOK_URL, json={
            "filename": filename,
            "destination": destination,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, timeout=10)
    except requests.RequestException as e:
        print(f"  n8n notify error: {e}")


# ── SCAN SUBFOLDERS DYNAMICALLY ───────────────────────────────────────────────
def get_available_folders():
    """Return all subfolders (relative paths) inside WATCH_FOLDER, excluding SKIP_FOLDERS."""
    result = []
    for root, dirs, _ in os.walk(WATCH_FOLDER):
        # Remove skipped folders so os.walk doesn't descend into them
        dirs[:] = [
            d for d in dirs if d not in SKIP_FOLDERS and not d.startswith(".")]

        rel_root = os.path.relpath(root, WATCH_FOLDER)
        if rel_root == ".":
            continue  # skip the root itself

        result.append(rel_root.replace("\\", "/"))

    return sorted(result)


# ── TOOLS ────────────────────────────────────────────────────────────────────
def move_file(filename: str, destination_rel: str):
    """Move a loose file into a subfolder (relative path like 'linearalgebra/assignment')."""
    src = os.path.join(WATCH_FOLDER, filename)
    dst_dir = os.path.join(WATCH_FOLDER, destination_rel)

    if not os.path.isdir(dst_dir):
        return f"ERROR: Folder '{destination_rel}' does not exist."
    if not os.path.isfile(src):
        return f"ERROR: File '{filename}' not found."

    shutil.move(src, os.path.join(dst_dir, filename))
    notify_n8n(filename, destination_rel)
    return f"Moved '{filename}' → {destination_rel}/"


def ask_user(filename: str, folders: list):
    """Ask the user interactively which folder to use."""
    print(f"\n  Can't classify: '{filename}'")
    print("  Available folders:")
    for i, f in enumerate(folders):
        print(f"    {i+1}. {f}")
    choice = input("  Type folder name or number (or 'skip'): ").strip()

    if choice.lower() == "skip":
        return None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(folders):
            return folders[idx]
    # Check if typed name matches
    for f in folders:
        if choice.lower() in f.lower():
            return f
    return None


# ── SUBFOLDER TYPE KEYWORDS ──────────────────────────────────────────────────
SUBFOLDER_KEYWORDS = {
    "assignment": ["assig", "assignment", "homework", "hw", "task", "submit"],
    "lecture":    ["lecture", "lec", "slides", "notes", "week"],
    "practical":  ["practical", "prac", "lab", "matlab", "workshop"],
    "projects":   ["project", "proj"],
    "workshops":  ["workshop", "ws", "tute", "tutorial"],
}


def keyword_classify_full(filename: str, folders: list):
    """Try to match both subject AND subfolder type from filename keywords."""
    name_lower = filename.lower()

    matched_subject = None
    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            matched_subject = subject
            break

    matched_type = None
    for subfolder_type, keywords in SUBFOLDER_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            matched_type = subfolder_type
            break

    if matched_subject and matched_type:
        candidate = f"{matched_subject}/{matched_type}"
        if candidate in folders:
            return candidate

    if matched_subject and matched_subject in folders:
        return matched_subject

    return None


# ── LLM CLASSIFIER ───────────────────────────────────────────────────────────
def ask_llm(filename: str, folders: list) -> str:
    """Send filename to Ollama and return the best matching folder path."""
    folder_list = "\n".join(f"- {f}" for f in folders)
    prompt = (
        f'You are a file sorter for a Year 1 university student at the University of Melbourne.\n\n'
        f'The student dropped a file called: "{filename}"\n\n'
        f'Available folders (subject/type format):\n{folder_list}\n\n'
        'Pick the MOST SPECIFIC folder that best matches this file.\n'
        'For example, if it looks like a linear algebra assignment, '
        'pick "linearalgebra/assignment" not just "linearalgebra".\n\n'
        'Reply with ONLY the exact folder path from the list above, nothing else.\n'
        'If you truly cannot decide, reply with exactly: ask_user'
    )

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }, timeout=30)
        reply = response.json()["message"]["content"].strip().strip('"').strip("'")

        # Find best match from available folders
        reply_lower = reply.lower()
        for folder in folders:
            if folder.lower() == reply_lower:
                return folder
        # Partial match fallback
        for folder in folders:
            if reply_lower in folder.lower() or folder.lower() in reply_lower:
                return folder
    except requests.RequestException as e:
        print(f"  LLM error: {e}")

    return "ask_user"


# ── MAIN CLASSIFY + MOVE ──────────────────────────────────────────────────────
def classify_and_move(filename: str):
    """Classify a new file and move it to the appropriate subfolder."""
    if filename.startswith(".") or filename.startswith("~"):
        return
    if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
        return

    folders = get_available_folders()
    if not folders:
        print("  No subfolders found to sort into.")
        return

    print(f"\nNew file: '{filename}'")

    # Try keyword match first (fast, free)
    folder = keyword_classify_full(filename, folders)
    if folder:
        print(f"  Keyword match → {folder}/")
    else:
        print("  Asking LLM to classify...")
        folder = ask_llm(filename, folders)

    if folder == "ask_user":
        folder = ask_user(filename, folders)
        if folder is None:
            print("  Skipped.")
            return

    result = move_file(filename, folder)
    print(f"  {result}")


# ── WATCHDOG ──────────────────────────────────────────────────────────────────
class FileSorterHandler(FileSystemEventHandler):
    """Watchdog handler that triggers file classification on new file creation."""

    def on_created(self, event):
        """Handle file creation events in the watch folder."""
        if event.is_directory:
            return
        parent = os.path.dirname(event.src_path)
        if os.path.abspath(parent) != os.path.abspath(WATCH_FOLDER):
            return
        time.sleep(1)  # wait for file to finish writing
        classify_and_move(os.path.basename(event.src_path))


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("File Sorter Agent running (press Ctrl+C to stop)")
    print(f"Watching: {WATCH_FOLDER}")
    print(f"Folders detected: {get_available_folders()}\n")

    observer = Observer()
    observer.schedule(FileSorterHandler(), WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nAgent stopped.")

    observer.join()
