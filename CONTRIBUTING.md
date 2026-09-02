# Contributing to Bailando Solo

Thanks for your interest in contributing! 🎶

## Quick Reference

| What you need | Where to find it |
|---|---|
| **Full project rules & conventions** | [`GEMINI.md`](GEMINI.md) |
| **Architecture & API reference** | [`docs/architecture.md`](docs/architecture.md) |
| **Development setup guide** | [`docs/guides/development.md`](docs/guides/development.md) |
| **Testing checklist** | [`docs/guides/testing.md`](docs/guides/testing.md) |
| **Theme creation rules** | [`ui/src/assets/styles/THEME_GUIDE.md`](ui/src/assets/styles/THEME_GUIDE.md) |
| **Roadmap & backlog** | [`docs/roadmap.md`](docs/roadmap.md) |

## Where Things Go

| What you're adding | Where it goes |
|---|---|
| New API endpoint | `server/routes/<domain>.py` — add to existing blueprint or create a new one |
| New Vue component | `ui/src/components/<ComponentName>.vue` |
| New API client function | `ui/src/services/<ServiceName>.js` |
| New CSS theme | `ui/src/assets/styles/theme-<name>.css` + import in `ui/src/main.js` |
| New theme JS animation | `ui/src/assets/js/<theme>-theme.js` |
| New standalone page | `static/<page>.html` + route in `server/routes/mobile.py` |
| Configuration constant | `server/config.py` |

## Commit Convention

```
<type>(<scope>): <description>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`  
**Scopes:** `backend`, `frontend`, `electron`, `mobile`, `build`, `ci`, `docs`

## Rules

- **No bare `except:`** — always catch specific exceptions
- **No hardcoded port** — use `server.config.PORT`
- **No hardcoded paths** — use `server.config.*_DIR` constants
- **Frontend API calls** — use relative URLs (`/api/...`), never `http://localhost:5001`
- **Thread safety** — use `server.state` functions for shared mutable state
- **CSS Themes** — ONLY override CSS variables, never write class selectors
