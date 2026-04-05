---
name: linkedin
description: Use when the user wants to write a LinkedIn post, announce a project, share a certification, draft a post from a GitHub commit, or turn any technical update into professional content.
argument-hint: "project details, commit message, cert name, or topic"
disable-model-invocation: true
---

## What This Skill Does

Transforms raw input — project details, GitHub commits, certifications, images, or topics — into 3 distinct LinkedIn post drafts using a Scroll-Stop framework. Each draft uses a different hook structure so the variations are genuinely different, not just rephrased.

Drafts are natural and human-sounding. No PR bot language. No AI smell.

---

## Step 1: Get the Input

If `$ARGUMENTS` is provided, detect the input type:

- **File path** (ends in `.py`, `.js`, `.md`, etc.): Read the file, extract the purpose and key technical decisions as the raw input.
- **Git commit hash** (7+ hex chars): Run `git show --stat $ARGUMENTS` and `git log -1 --format=%B $ARGUMENTS` to extract the commit message and changed files as raw input.
- **URL** (starts with `http`): Fetch the page title and description as context.
- **Plain text**: Use it directly as the raw input.

If no arguments, ask:
1. "What do you want to post about? (paste a description, commit message, cert name, file path, or just describe it)"
2. "Any specific detail you want highlighted — a bug you fixed, a tool you used, something that surprised you?"

---

## Step 2: Extract the Core

Before writing anything, identify two things from the input:

**Technical Core (the what):**
- The specific tool, language, platform, or concept involved
- One concrete technical hurdle or 'gotcha' — a specific error, config step, version conflict, or unexpected behaviour. If the user didn't mention one, ask: "Was there anything that tripped you up or surprised you while building this?"

**Human Effort (the how):**
- Why the user built or learned this — what motivated it
- What changed or improved as a result

This extraction is the "Proof of Work." It's what makes the post read like it was written by a developer, not a PR bot.

---

## Step 3: Generate 3 Drafts

Each draft must use a different hook structure. Do not reuse the same opening style across drafts.

### Variation 1 — The Contrarian
Opens by challenging a common belief, oversimplification, or gap in standard tutorials/advice.

Example openings:
- "Most tutorials skip the part where..."
- "Everyone talks about [X]. Nobody talks about what happens when..."
- "The AWS docs make this look simple. It's not."

### Variation 2 — The Direct Result
Opens with the concrete outcome. No build-up. No context. Just the result — then explain how.

Example openings:
- "I just [specific result] using [specific tool]."
- "Built something today that [specific outcome]."
- "Took [X] from [old state] to [new state]."

### Variation 3 — The Why
Opens with the motivation, frustration, or goal that started the whole thing. Personal but grounded.

Example openings:
- "The reason I built this was..."
- "I kept running into [problem] every time I tried to [task]."
- "Wanted to understand [X] properly, not just use it."

---

## Step 4: Apply Scroll-Stop Structure to Each Draft

Each draft must follow this structure:

**Hook** (1–2 sentences max)
— Use the assigned variation type above. Must stop the scroll.

**Value/Insight** (3–6 sentences)
— Explain what was built/learned. Include the specific technical hurdle from Step 2.
— Answer: "So what? Why should a recruiter or peer care about this specific update?"
— Use 1–2 sentence paragraphs. Maximize white space. Mix short punchy sentences with longer explanatory ones (Gary Provost rhythm).

**CTA** (1–2 sentences)
— Natural close. Ask a genuine question, invite feedback, or state what's next.
— Never force it. No "Let me know your thoughts in the comments below!"

**Hashtags**
— 3–5 relevant hashtags. Mix broad (#AWS, #Python) with specific (#AWSDVA #CloudEngineer).

---

## Step 5: Apply the Anti-AI Filter

Before outputting any draft, run every sentence through these checks:

**Hard ban list — delete or rewrite any sentence containing:**
- Excited / Thrilled / Delighted / Humbled / Blessed
- Delighted / Navigating / Unlocking / Empowering / Tapestry / Masterclass
- "In today's fast-paced world" / "In the ever-evolving landscape"
- "I'm happy to share" / "I'm proud to announce"
- Any variation of "journey"

**Emoji rules:**
- Max 2–3 per post total
- Only as bullet points (→, ✅) or single emphasis — never at the end of every sentence
- When in doubt, use none

**Sentence rhythm check:**
- No 3+ sentences in a row of the same length
- Mix short. Then a longer one that adds context or nuance. Then short again.

**"So what?" test:**
- Every draft must have a clear answer to: "Why should someone reading this care?"
- If the draft reads like a press release, rewrite it to sound like a Slack message to a smart colleague.

---

## Step 6: Present Drafts

Show all 3 drafts clearly labelled. After each draft, show the hashtags for that variation.

Then ask:
- "Which one feels closest to your voice?"
- "Want me to adjust the tone, swap the hook, or change the technical detail highlighted?"

Iterate until the user is happy with one.

---

## Step 7: Save to Vault

Save all 3 drafts to:
`C:\Users\<your-username>\OneDrive\Documents\Obsidian\obsidianvault\linkedin\[topic-slug]-[date].md`

Use this Obsidian frontmatter so notes are searchable by date, tag, and type:

```markdown
---
date: [YYYY-MM-DD]
type: linkedin-draft
topic: [topic slug]
tags: [extracted hashtags without #]
status: draft
---
```

Tell the user: "Saved to your vault at linkedin/[filename]"

---

## Notes

- **Never post directly** — always a draft for the user to review and post manually
- **Never glaze** — if a draft sounds hyped or corporate, it failed the filter
- **Proof of Work is mandatory** — every post must contain one specific technical detail. Generic posts get ignored.
- **3 variations must be genuinely different** — different hook type, different angle, different opening sentence structure
- If the user provides a GitHub commit message, extract the technical core from the commit body and ask for any gotchas from that session
- Posts should feel like they were written by a developer who happens to be good at writing — not by a marketer who learned to code
