# Contributing to Bailando Solo

## For AI Agents and Humans

### Where things go

| What you're adding | Where it goes |
|---|---|
| New API endpoint | `server/routes/<domain>.py` — add to existing blueprint or create a new one |
| New Vue component | `ui/src/components/<ComponentName>.vue` |
| New API client function | `ui/src/services/<ServiceName>.js` |
| New CSS theme | `ui/src/assets/styles/theme-<name>.css` + import in `ui/src/main.js` |
| New theme JS animation | `ui/src/assets/js/<theme>-theme.js` |
| New standalone page | `static/<page>.html` + route in `server/routes/mobile.py` |
| Configuration constant | `server/config.py` |

### Naming conventions

- **Python files**: `snake_case.py`
- **Vue components**: `PascalCase.vue`
- **CSS themes**: `theme-<name>.css`
- **API endpoints**: `/api/<domain>/<action>`
- **Blueprint variables**: `<domain>_bp`

### Adding a new route domain

1. Create `server/routes/<domain>.py`
2. Define a Blueprint: `<domain>_bp = Blueprint('<domain>', __name__)`
3. Add routes using `@<domain>_bp.route()`
4. Register in `server/__init__.py`: `app.register_blueprint(<domain>_bp)`

### Rules

- **No bare `except:`** — always catch specific exceptions
- **No hardcoded port** — use `server.config.PORT`
- **No hardcoded paths** — use `server.config.*_DIR` constants
- **Frontend API calls** — use relative URLs (`/api/...`), never `http://localhost:5001`
- **Thread safety** — use `server.state` functions for shared mutable state
