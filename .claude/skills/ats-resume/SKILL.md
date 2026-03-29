---
name: ats-resume
description: Use to generate, audit, or format a resume. Enforces verified ATS-compliant two-column layout standard with section labels left, content right. Works for any field.
disable-model-invocation: true
---

## Role
You are an ATS resume processor. Your objective is structural compliance, keyword alignment, and metric-driven bullet point generation following the verified two-column ATS layout standard.

## ATS Format Standard

Output resumes as HTML files compiled to PDF via headless Chrome (full Unicode support). The layout is a verified ATS-compliant two-column table structure:

- **Header:** Bold centered name + role/degree subtitle on same line. Contact info centered below.
- **Left column (24%):** Section labels (ALL CAPS, bold) and dates.
- **Right column (76%):** All content — profile text, skills grid, bullets, descriptions.
- **Section separators:** `<hr/>` between every section.
- **Skills and Languages:** Two-column grid table inside the right column.
- **Section order:** LINKS → PROFILE → TECHNICAL SKILLS → PROJECTS → PROFESSIONAL EXPERIENCE → EDUCATION → LANGUAGES

Omit any section with no content. LINKS is optional (only include if person has LinkedIn/GitHub/portfolio).

## Bullet Point Formula

All experience and project bullets: `[Action Verb] + [Task] + [Quantifiable Result] + [Tech Stack]`

- Weak: "Worked on a capstone project for school."
- Strong: "Architected a full-stack AI marketplace integrating ML phishing detection, reducing false-positive flags using Python and React."

Delete all subjective filler: "fast learner", "team player", "good interpersonal", "hardworking", "able to work under pressure" — these kill ATS scores.

For non-tech fields (e.g. Quantity Surveying, Finance), adapt TECHNICAL SKILLS to domain keywords (e.g. Bill of Quantities, PAM Contract, Cost Estimation, SMM).

## Execution Flow

### Step 1: Data Ingestion
Parse the provided resume file or raw experience. Extract competencies, timelines, and metrics. Discard filler.

### Step 2: Ask for Target Role
If not already provided, ask: "What role is this resume targeting?"

### Step 3: Generate HTML Resume File

Output a complete HTML file at `resume/[firstname]_ats_resume.html` using the template and CSS below. Fill in all sections from the parsed resume data.

**HTML Template:**

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page { size: A4; margin: 1.2cm 1.3cm 1.2cm 1.3cm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #000; line-height: 1.3; }
h1 { font-size: 12.5pt; font-weight: bold; text-align: center; margin: 0 0 3px 0; }
p.contact { text-align: center; font-size: 9.5pt; margin: 0 0 8px 0; }
table.row { width: 100%; border-collapse: collapse; margin: 2px 0; }
table.row td { vertical-align: top; padding: 1px 0; }
td.lbl { width: 24%; font-weight: bold; font-size: 8pt; letter-spacing: 0; padding-right: 10px; }
td.date { width: 24%; font-size: 9pt; color: #333; padding-right: 10px; }
td.cnt { width: 76%; }
table.title { width: 100%; border-collapse: collapse; margin: 0 0 2px 0; }
table.title td { padding: 0; vertical-align: baseline; }
td.tloc { text-align: right; font-size: 9pt; color: #333; white-space: nowrap; padding-left: 6px; }
table.grid { width: 100%; border-collapse: collapse; }
table.grid td { width: 50%; padding: 0 4px 2px 0; font-size: 9.5pt; }
hr { border: none; border-top: 1px solid #000; margin: 6px 0; }
a { color: #000; text-decoration: none; }
b { font-weight: bold; }
ul { margin: 3px 0 4px 0; padding-left: 16px; }
li { margin-bottom: 2px; }
p { margin: 2px 0 3px 0; }
</style>
</head>
<body>

<h1>FULL NAME, Role or Degree Title</h1>
<p class="contact">City, Country | Phone | email@email.com | <a href="https://linkedin.com/in/...">linkedin.com/in/...</a> | <a href="https://github.com/...">github.com/...</a></p>

<!-- LINKS (omit entire block if no links) -->
<table class="row"><tr>
  <td class="lbl">LINKS</td>
  <td class="cnt"><a href="https://linkedin.com/in/...">linkedin.com/in/...</a> &nbsp;|&nbsp; <a href="https://github.com/...">github.com/...</a></td>
</tr></table><hr/>

<!-- PROFILE -->
<table class="row"><tr>
  <td class="lbl">PROFILE</td>
  <td class="cnt">3-4 sentence keyword-rich professional summary here.</td>
</tr></table><hr/>

<!-- TECHNICAL SKILLS — use domain keywords for non-tech fields -->
<table class="row"><tr>
  <td class="lbl">TECHNICAL SKILLS</td>
  <td class="cnt">
    <table class="grid">
      <tr><td>Skill 1</td><td>Skill 2</td></tr>
      <tr><td>Skill 3</td><td>Skill 4</td></tr>
    </table>
  </td>
</tr></table><hr/>

<!-- PROJECTS — omit section if no projects -->
<table class="row"><tr>
  <td class="lbl">PROJECTS</td>
  <td class="cnt"></td>
</tr></table>
<table class="row"><tr>
  <td class="date">Mon Year &#8212; Mon Year</td>
  <td class="cnt">
    <table class="title"><tr>
      <td><b>Project Name</b></td>
      <td class="tloc">Location</td>
    </tr></table>
    <p>Action verb + task + result + tech stack.</p>
    <b>Sub-feature or Component Name</b>
    <p>Action verb + task + result + tech stack.</p>
  </td>
</tr></table><hr/>

<!-- PROFESSIONAL EXPERIENCE — omit section if no experience -->
<table class="row"><tr>
  <td class="lbl">PROFESSIONAL EXPERIENCE</td>
  <td class="cnt"></td>
</tr></table>
<table class="row"><tr>
  <td class="date">Mon Year &#8212; Mon Year</td>
  <td class="cnt">
    <table class="title"><tr>
      <td><b>Role Title, Organisation Name</b></td>
      <td class="tloc">City, Country</td>
    </tr></table>
    <ul>
      <li>Action verb + task + quantifiable result + method/tool.</li>
      <li>Action verb + task + quantifiable result + method/tool.</li>
    </ul>
  </td>
</tr></table><hr/>

<!-- EDUCATION -->
<table class="row"><tr>
  <td class="lbl">EDUCATION</td>
  <td class="cnt"></td>
</tr></table>
<table class="row"><tr>
  <td class="date">Mon Year</td>
  <td class="cnt">
    <table class="title"><tr>
      <td><b>Degree or Qualification, Institution Name</b></td>
      <td class="tloc">City</td>
    </tr></table>
    <p>Score, scholarship, key modules, or notable achievement.</p>
  </td>
</tr></table><hr/>

<!-- LANGUAGES -->
<table class="row"><tr>
  <td class="lbl">LANGUAGES</td>
  <td class="cnt">
    <table class="grid">
      <tr><td>English (Fluent)</td><td>Malay (Fluent)</td></tr>
    </table>
  </td>
</tr></table>

</body>
</html>
```

### Step 4: Compile HTML to PDF

Write and run this Python compile script at `resume/compile_tmp.py`:

```python
import subprocess, os, time, json, base64, threading, shutil
import requests
import websocket

html_path = os.path.abspath("resume/[firstname]_ats_resume.html")
pdf_path  = os.path.abspath("resume/[firstname]_ats_resume.pdf")
chrome    = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
port      = 9222
tmp_dir   = r"C:\Temp\chrome_pdf_tmp"

if os.path.exists(pdf_path):
    os.remove(pdf_path)
shutil.rmtree(tmp_dir, ignore_errors=True)
os.makedirs(tmp_dir, exist_ok=True)

proc = subprocess.Popen([
    chrome, "--headless", "--disable-gpu", "--no-sandbox",
    f"--remote-debugging-port={port}", f"--user-data-dir={tmp_dir}",
    "--remote-allow-origins=*",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws_url = None
for _ in range(30):
    time.sleep(0.5)
    try:
        tabs = requests.get(f"http://localhost:{port}/json/list", timeout=2).json()
        pages = [t for t in tabs if t.get("type") == "page"]
        if pages:
            ws_url = pages[0]["webSocketDebuggerUrl"]
            break
    except Exception:
        continue

if not ws_url:
    proc.terminate()
    raise RuntimeError("Chrome debug server did not start")

done  = threading.Event()
error = []

def send(ws, id_, method, params=None):
    ws.send(json.dumps({"id": id_, "method": method, "params": params or {}}))

def on_message(ws, msg):
    data   = json.loads(msg)
    mid    = data.get("id")
    method = data.get("method", "")
    if mid == 1:
        send(ws, 2, "Page.navigate",
             {"url": "file:///" + html_path.replace("\\", "/")})
    elif method == "Page.loadEventFired":
        send(ws, 3, "Page.printToPDF", {
            "displayHeaderFooter": False, "printBackground": True,
            "paperWidth": 8.27, "paperHeight": 11.69,
            "marginTop": 0.5, "marginBottom": 0.5,
            "marginLeft": 0.5, "marginRight": 0.5,
        })
    elif mid == 3:
        if "error" in data:
            error.append(str(data["error"]))
        else:
            with open(pdf_path, "wb") as f:
                f.write(base64.b64decode(data["result"]["data"]))
        done.set()

def on_error(ws, err):
    error.append(str(err))
    done.set()

def on_open(ws):
    send(ws, 1, "Page.enable")

ws_app = websocket.WebSocketApp(ws_url, on_open=on_open,
                                on_message=on_message, on_error=on_error)
t = threading.Thread(target=ws_app.run_forever)
t.daemon = True
t.start()

if not done.wait(timeout=30):
    print("ERROR: Timed out waiting for Chrome")
elif error:
    print(f"ERROR: {error[0]}")
else:
    print(f"SUCCESS: {pdf_path}")

ws_app.close()
proc.terminate()
shutil.rmtree(tmp_dir, ignore_errors=True)
```

Dependencies: `pip install requests websocket-client` (Python 3.12)

Run from the project root directory. Delete `resume/compile_tmp.py` after successful compilation.

### Step 5: ATS Score Check

After the PDF is compiled, automatically run the ATS score checker:

```bash
"C:/Users/<your-username>/AppData/Local/Programs/Python/Python312/python.exe" resume/resume_builder.py score --resume resume/[firstname]_ats_resume.html --job "[full job description]"
```

Report to the user:
- Score percentage
- Matched keywords
- Top 5 missing keywords to consider adding

### Step 6: Ask for Tailoring

After showing the score, ask the user:
> "Do you want Ollama to suggest a rewritten profile and missing skills based on this job description? (requires Ollama running)"

If yes, run:

```bash
"C:/Users/<your-username>/AppData/Local/Programs/Python/Python312/python.exe" resume/resume_builder.py tailor --resume resume/[firstname]_ats_resume.html --job "[full job description]"
```

If Ollama is not running, tell the user:
> "Start Ollama first: run `ollama serve` in a separate terminal, then try again."

### Step 7: Final Report

Tell the user:
- Full file path of the output PDF
- ATS score + top missing keywords
- Which sections were included / omitted and why

## Rules

- Maximum 3 bullet points per role or project entry
- Dates use en-dash: `Mon Year &#8212; Mon Year` (HTML entity for —)
- No emojis, photos, subjective adjectives, or references section
- Location uses `table.title` with `td.tloc` (text-align: right) — always include for roles, projects, and degrees. Never use `span.loc` or float.
- For single-date entries (e.g. graduation), use just `Mon Year` in the date column
- Merge multi-line subject lists into one line: `HL: X, Y, Z | SL: A, B, C`
- Project sub-entries use `<b>Name</b>` + `<p>description</p>` — NOT h3 tags
- All links (LinkedIn, GitHub, portfolio) must be wrapped in `<a href="...">` tags so they are clickable in the PDF. Style with `a { color: #000; text-decoration: none; }`. If the source document does not include a full URL, ask the user before omitting the link.
