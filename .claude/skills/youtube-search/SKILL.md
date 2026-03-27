---
name: youtube-search
description: Use when searching YouTube for videos on a topic. Returns structured video results including titles, URLs, duration, and descriptions.
argument-hint: [search query]
disable-model-invocation: true
---

## What This Skill Does

Searches YouTube using yt-dlp and returns structured results for a given query. Used as a sub-skill by the youtube-pipeline skill, but can also be called directly.

## Python Executable

Always use: `C:\Users\dnialhziem\AppData\Local\Programs\Python\Python312\python.exe`

## Execution Flow

### Step 1: Get the Query

If `$ARGUMENTS` is provided, use it as the search query.
If not, ask the user: "What do you want to search for on YouTube?"

### Step 2: Run the Search

Execute this command (replace QUERY with the actual search terms):

```bash
C:\Users\dnialhziem\AppData\Local\Programs\Python\Python312\python.exe -m yt_dlp "ytsearch10:QUERY" --dump-json --flat-playlist --no-warnings 2>/dev/null
```

This returns up to 10 results as JSON lines.

### Step 3: Parse and Format Results

For each result extract:
- `title` — video title
- `webpage_url` — full YouTube URL
- `duration_string` — length of video
- `view_count` — number of views
- `uploader` — channel name
- `description` — first 200 chars of description

Output in this format:

```
## YouTube Search Results: [query]

1. **[title]**
   - Channel: [uploader]
   - Duration: [duration_string]
   - Views: [view_count]
   - URL: [webpage_url]
   - Description: [description snippet]

2. ...
```

### Step 4: Return Results

Return the formatted list. If called from youtube-pipeline, pass the URLs directly to the next step.

## Notes

- If yt-dlp returns no results, tell the user and suggest rephrasing the query
- Max 10 results per search
- Do not download any video content — flat-playlist and dump-json only
