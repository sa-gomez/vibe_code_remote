# vibe-code-remote

## Dev server

Package manager: `uv`. No `pip` binary in the venv — use `uv add <pkg>` to install packages.

Start Flask (must specify `--app main`; no auto-discovery):
```
.venv/bin/flask --app main run
```

If port 5000 is already in use (old process still running):
```
lsof -ti :5000 | xargs kill -9
```

Then start again. The server takes ~5–8 seconds to load the sentence-transformers model before it's ready.

Run in the background:
```
.venv/bin/flask --app main run &
```

## Architecture

- `main.py` — Flask app + all matching logic
- `templates/match.html` — recruiter job matcher UI
- `templates/index.html` — portfolio site
- `data/body_of_work.md` — Aaron's full background (used by all matchers)

## /match — matching methods

Three strategies toggled via radio buttons, all returning `{match_level, matching_areas, gaps, summary}`:

| Method | Function | Notes |
|--------|----------|-------|
| Claude API | `evaluate_match()` | Needs `ANTHROPIC_API_KEY` |
| Keywords (TF-IDF) | `evaluate_match_tfidf()` | Free, lexical only |
| Embeddings | `evaluate_match_embeddings()` | `all-MiniLM-L6-v2`, loaded at startup |

Embeddings model and chunk vectors are pre-computed at startup and reused across requests.
