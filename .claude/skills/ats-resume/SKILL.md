---
name: ats-resume
description: Use to generate, audit, or format a resume. Enforces verified ATS-compliant two-column layout standard with section labels left, content right. Works for any field.
disable-model-invocation: true
---

## Supporting Files

- [template.html](template.html) — ATS-compliant HTML resume template. Load this when generating a new resume in Step 3.
- [compile.py](compile.py) — Headless Chrome PDF compiler. Run this in Step 4 instead of writing a compile script from scratch.

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

Load [template.html](template.html) as the base structure. Fill in all sections from the parsed resume data. Output the completed HTML to `resume/[firstname]_ats_resume.html`.

### Step 4: Compile HTML to PDF

Run the bundled compile script (do NOT write a new one):

```bash
"C:/Users/dnialhziem/AppData/Local/Programs/Python/Python312/python.exe" .claude/skills/ats-resume/compile.py "resume/[firstname]_ats_resume.html" "resume/[firstname]_ats_resume.pdf"
```

Dependencies: `pip install requests websocket-client` (Python 3.12)

If Chrome is not installed, tell the user: "Chrome is required for PDF compilation. Install it or open the HTML file in a browser and print to PDF."

### Step 5: ATS Score Check

After the PDF is compiled, automatically run the ATS score checker:

```bash
"C:/Users/dnialhziem/AppData/Local/Programs/Python/Python312/python.exe" resume/resume_builder.py score --resume resume/[firstname]_ats_resume.html --job "[full job description]"
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
"C:/Users/dnialhziem/AppData/Local/Programs/Python/Python312/python.exe" resume/resume_builder.py tailor --resume resume/[firstname]_ats_resume.html --job "[full job description]"
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
