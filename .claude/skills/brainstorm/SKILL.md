---
name: brainstorm
description: Use when someone asks to brainstorm, explore ideas, or ideate on any topic. Guides a deep, iterative idea generation session with pros/cons evaluation.
---

## What This Skill Does

Runs an interactive brainstorming session on any topic. Asks clarifying questions first, generates ideas in rounds with pros/cons, iterates conversationally, and saves a summary file to the Obsidian vault that improves future sessions.

## Supporting Files

- Past session summaries are stored in `C:\Users\<your-username>\OneDrive\Documents\Obsidian\obsidianvault\brainstorm\`. Load any relevant ones before starting if the topic overlaps with a previous session.

## Execution Flow

### Step 1: Load Past Context

Check `C:\Users\<your-username>\OneDrive\Documents\Obsidian\obsidianvault\brainstorm\` for any summary files. If there are past sessions related to the current topic, read them and use their insights to inform this session. Tell the user if you found relevant past sessions.

### Step 2: Ask What to Brainstorm

Ask the user: **"What do you want to brainstorm today?"**

Then ask 2–3 clarifying questions to understand context deeply before generating ideas. Examples:
- What's the goal or outcome you're hoping for?
- Are there any constraints (time, resources, scope)?
- Have you already tried any approaches? What happened?

Do NOT generate ideas yet. Understand first.

### Step 3: Generate First Round of Ideas

Produce **5–7 ideas** based on what you've learned. For each idea:
- Give it a clear, memorable name
- Write 2–3 sentences explaining it with enough depth to be useful
- List **pros** (2–3 bullet points)
- List **cons** (2–3 bullet points)

Format:
```
### [Idea Name]
[2–3 sentence explanation]

**Pros:**
- ...

**Cons:**
- ...
```

### Step 4: Iterate Conversationally

After presenting ideas, ask:
- Which ideas resonate? Which don't?
- Do you want to go deeper on any of them?
- Should I generate a new angle or build on what's here?

Keep iterating based on replies. Each round should refine, not just repeat. Build on the user's responses — if they like an idea, explore it further; if they dislike one, understand why and adjust.

### Step 5: Save Session Summary

When the user is done (they say something like "that's enough", "wrap it up", "save this"), save a summary to `C:\Users\<your-username>\OneDrive\Documents\Obsidian\obsidianvault\brainstorm\[topic-slug]-[date].md` using the template below.

Use today's date in YYYY-MM-DD format for the filename. Slugify the topic (lowercase, hyphens, no special chars).

**Summary Template:**

```markdown
# Brainstorm: [Topic]
**Date:** [YYYY-MM-DD]

## Context
[What the user was trying to achieve, constraints, background from the clarifying questions]

## Ideas Explored

### [Idea Name]
[Brief description]
- **Pros:** ...
- **Cons:** ...
- **Verdict:** [User's reaction — liked, disliked, wants to explore further, etc.]

[Repeat for each idea discussed]

## Key Insights
[2–4 bullet points summarizing the most useful things that came out of this session]

## Next Steps
[Any actions or directions the user said they'd pursue]
```

Tell the user the file was saved and where.

## Notes

- **Never make the final decision.** Always present options and reasoning. The user decides.
- **Never be too brief.** Each idea needs enough depth to be genuinely useful, not just a label.
- **Stay focused.** If the conversation drifts off-topic, gently redirect back to the brainstorm goal.
- **5–7 ideas per round** is the target. More overwhelms; fewer underwhelms.
- The session is conversational — don't dump everything at once. Wait for the user to respond between rounds.
