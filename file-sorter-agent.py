"""File sorter agent: watches the year1 folder and auto-sorts new files into subject subfolders."""

import os
import shutil
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── CONFIG ──────────────────────────────────────────────────────────────────
WATCH_FOLDER = r"C:\Users\dnialhziem\OneDrive - The University of Melbourne\unimelb\year1"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral:7b"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sorter_log.txt")

def log(msg: str):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# Folders to skip when scanning (won't descend into these)
SKIP_FOLDERS = {"PYTHON-BUDDY"}

# Specific subfolders inside SKIP_FOLDERS that ARE valid destinations
EXTRA_FOLDERS = ["PYTHON-BUDDY/resume"]

# Temp/incomplete download extensions to ignore
IGNORE_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}

# Filename substrings → fixed destination folder (bypasses folder scan + LLM)
FIXED_ROUTES = {
    "resume":      "PYTHON-BUDDY/resume",
    "cv":          "PYTHON-BUDDY/resume",
    "coverletter": "PYTHON-BUDDY/resume",
    "cover letter":"PYTHON-BUDDY/resume",
    "linkedin":    "PYTHON-BUDDY/resume",
}

# Subject keywords for keyword classifier
SUBJECT_KEYWORDS = {
    "blaw":            ["blaw", "contract", "legal"],
    "comp 10001":      ["comp10001", "comp 10001", "computing", "algorithm"],
    "linearalgebra":   ["linearalgebra", "linear algebra", "mast10007", "mast 10007", "mast10", "algebra", "matrix", "vector", "eigen", "s2_2026"],
    "python learning": ["python", "exercise", "practice"],
    "scie10005":       ["scie10005", "scie 10005", "tstw", "biology", "climate", "understanding climate"],
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

        rel_posix = rel_root.replace("\\", "/")
        if rel_posix.count("/") >= 2:
            dirs[:] = []  # don't descend further
            continue

        result.append(rel_posix)

    # Add whitelisted subfolders from inside SKIP_FOLDERS
    for extra in EXTRA_FOLDERS:
        full_path = os.path.join(WATCH_FOLDER, extra.replace("/", os.sep))
        if os.path.isdir(full_path) and extra not in result:
            result.append(extra)

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

    # Retry up to 5 times if the file is still being written
    for attempt in range(5):
        try:
            name, ext = os.path.splitext(filename)
            dst_path = os.path.join(dst_dir, filename)
            # If destination already exists, append a counter
            counter = 1
            while os.path.exists(dst_path):
                dst_path = os.path.join(dst_dir, f"{name}_{counter}{ext}")
                counter += 1
            shutil.move(src, dst_path)
            notify_n8n(filename, destination_rel)
            moved_name = os.path.basename(dst_path)
            return f"Moved '{filename}' -> {destination_rel}/{moved_name}"
        except PermissionError:
            if attempt < 4:
                time.sleep(2)
            else:
                return f"ERROR: File '{filename}' locked after 5 attempts — skipped."


UNCLASSIFIED_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_unclassified.txt")

def ask_user(filename: str, folders: list):
    """In background mode (no terminal), log the file and skip it instead of hanging on input()."""
    import sys
    if not sys.stdin.isatty():
        # Running as Task Scheduler background task — no terminal available
        with open(UNCLASSIFIED_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} — could not classify: {filename}\n")
        print(f"  No terminal — logged to _unclassified.txt and skipped.")
        return None

    # Interactive mode: ask user
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


# ── PDF TEXT EXTRACTOR ───────────────────────────────────────────────────────
def extract_pdf_text(filename: str, max_chars: int = 500) -> str:
    """Extract the first max_chars of text from a PDF file. Returns empty string on failure."""
    if not PDF_AVAILABLE:
        return ""
    filepath = os.path.join(WATCH_FOLDER, filename)
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) >= max_chars:
                break
        return text[:max_chars].strip()
    except Exception as e:
        log(f"  PDF read error: {e}")
        return ""


# ── LLM CLASSIFIER ───────────────────────────────────────────────────────────
def ask_llm(filename: str, folders: list, content: str = "") -> str:
    """Send filename (and optional file content) to Ollama and return the best matching folder path."""
    folder_list = "\n".join(f"- {f}" for f in folders)
    content_block = f'\n\nFile content preview:\n"""\n{content}\n"""' if content else ""
    prompt = (
        f'You are a file sorter for a Year 1 university student at the University of Melbourne.\n\n'
        f'The student dropped a file called: "{filename}"{content_block}\n\n'
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
        log(f"  LLM error: {e}")

    return "ask_user"


# ── MAIN CLASSIFY + MOVE ──────────────────────────────────────────────────────
def classify_and_move(filename: str):
    """Classify a new file and move it to the appropriate subfolder."""
    if filename.startswith(".") or filename.startswith("~") or filename.startswith("_"):
        return
    if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
        return

    # Check fixed routes (resume, CV, LinkedIn → always go to PYTHON-BUDDY/resume)
    name_lower = filename.lower()
    for kw, destination in FIXED_ROUTES.items():
        if kw in name_lower:
            log(f"Fixed route: '{filename}' -> {destination}/")
            result = move_file(filename, destination)
            log(f"  {result}")
            return

    folders = get_available_folders()
    if not folders:
        log("  No subfolders found to sort into.")
        return

    log(f"New file: '{filename}'")

    # Try keyword match first (fast, no Ollama needed)
    folder = keyword_classify_full(filename, folders)
    if folder:
        log(f"  Keyword match -> {folder}/")
    else:
        # For PDFs, extract text content to help Ollama classify accurately
        content = ""
        if filename.lower().endswith(".pdf"):
            content = extract_pdf_text(filename)
            if content:
                log(f"  Extracted PDF text ({len(content)} chars) — sending to LLM...")
            else:
                log("  PDF text extraction failed — using filename only...")
        else:
            log("  Asking LLM to classify...")
        folder = ask_llm(filename, folders, content)

    if folder == "ask_user":
        folder = ask_user(filename, folders)
        if folder is None:
            log("  Skipped.")
            return

    result = move_file(filename, folder)
    log(f"  {result}")


# ── WATCHDOG ──────────────────────────────────────────────────────────────────
class FileSorterHandler(FileSystemEventHandler):
    """Watchdog handler that triggers file classification on new file creation or move."""

    def _handle(self, path: str, is_directory: bool):
        if is_directory:
            return
        parent = os.path.dirname(path)
        if os.path.abspath(parent) != os.path.abspath(WATCH_FOLDER):
            log(f"  SKIP (not root): {parent}")
            return
        time.sleep(2)  # wait for file to finish writing (OneDrive sync delay)
        classify_and_move(os.path.basename(path))

    def on_created(self, event):
        """Handle file creation (copy-paste from different drive)."""
        log(f"EVENT created: {event.src_path}")
        self._handle(event.src_path, event.is_directory)

    def on_moved(self, event):
        """Handle file move/rename (cut-paste on same drive lands in WATCH_FOLDER)."""
        log(f"EVENT moved: {event.dest_path}")
        self._handle(event.dest_path, event.is_directory)


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
def scan_existing():
    """Sort any loose files already in WATCH_FOLDER at startup."""
    loose = [
        f for f in os.listdir(WATCH_FOLDER)
        if os.path.isfile(os.path.join(WATCH_FOLDER, f))
    ]
    if loose:
        log(f"Startup scan: {len(loose)} loose file(s) found")
        for f in loose:
            classify_and_move(f)
    else:
        log("Startup scan: folder is clean")


if __name__ == "__main__":
    log("File Sorter Agent started")
    log(f"Watching: {WATCH_FOLDER}")
    log(f"Folders: {get_available_folders()}")

    scan_existing()

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
