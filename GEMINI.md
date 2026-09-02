# Bailando Solo — Agent Rules

> **Read this file first.** It is the single source of truth for any AI agent working on this repository.

## Project Identity

**Bailando Solo** is a personal music downloader and player desktop app with a retro gaming aesthetic.

| Layer | Technology | Entry Point |
|---|---|---|
| Desktop shell | Electron 33 | `main.js` |
| Frontend | Vue 3 + Vite | `ui/src/App.vue` |
| Backend API | Python 3.10+ / Flask | `server.py` → `server/__init__.py` |
| Audio engine | yt-dlp + ffmpeg | called by `server/routes/downloads.py` |
| Mobile web | Standalone HTML | `static/mobile.html` |
| CI/CD | GitHub Actions | `.github/workflows/release.yml` |

**Current version:** 1.0.0  
**Architecture doc:** [`docs/architecture.md`](docs/architecture.md)

---

## Quick Start (Development)

```bash
# Option A: All-in-one
chmod +x start.sh && ./start.sh

# Option B: Manual (two terminals)
# Terminal 1 — Backend
source venv/bin/activate && python3 server.py

# Terminal 2 — Frontend + Electron
npm run dev
```

Frontend dev server: `http://localhost:5173` (proxies API to `:5001`)  
Backend API: `http://localhost:5001/api/...`

---

## Code Conventions

### Python (Backend)

- Files: `snake_case.py`
- New endpoints go in `server/routes/<domain>.py` as Flask Blueprints
- Register new blueprints in `server/__init__.py`
- **No bare `except:`** — always catch specific exceptions
- **No hardcoded port** — use `server.config.PORT`
- **No hardcoded paths** — use `server.config.*_DIR` constants
- **Thread safety** — use `server.state` functions for shared mutable state

### Vue / JavaScript (Frontend)

- Components: `PascalCase.vue` in `ui/src/components/`
- Services: `PascalCaseService.js` in `ui/src/services/`
- API calls: use relative URLs (`/api/...`), never `http://localhost:5001`
- Server URL resolution: use `ui/src/config.js` → `getServerUrl()`

### CSS Themes

- Files: `theme-<name>.css` in `ui/src/assets/styles/`
- **ONLY override CSS variables** — never write class selectors
- Use `body[data-theme="<name>"]` selector
- See [`ui/src/assets/styles/THEME_GUIDE.md`](ui/src/assets/styles/THEME_GUIDE.md) for the full spec
- Import new themes in `ui/src/main.js`

### Adding a New Feature (Checklist)

1. Backend route → `server/routes/<domain>.py` (Blueprint)
2. Register blueprint → `server/__init__.py`
3. Frontend service → `ui/src/services/<Name>Service.js`
4. Vue component → `ui/src/components/<Name>.vue`
5. Wire into `App.vue` or the relevant parent
6. Update `docs/architecture.md` API table if adding endpoints

---

## Git Conventions

### Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable releases. Tagged with `vX.Y.Z` |
| `develop` | Integration branch. All feature branches merge here |
| `feature/<name>` | New features. Branch from `develop`, merge back to `develop` |
| `fix/<name>` | Bug fixes. Branch from `develop` or `main` (hotfix) |
| `release/<version>` | Release candidates. Branch from `develop`, merge to `main` + tag |

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`  
**Scopes:** `backend`, `frontend`, `electron`, `mobile`, `build`, `ci`, `docs`

**Examples:**
```
feat(backend): add playlist reorder endpoint
fix(frontend): resolve audio not playing on first click
docs: update API reference in architecture.md
chore(build): upgrade electron-builder to v26
```

### Releases

- Tag format: `vX.Y.Z` (semantic versioning)
- CI automatically builds multi-platform installers on tag push
- Update `package.json` version before tagging
- Document changes in `docs/changelog.md`

---

## Project Structure Reference

```
BailandoSolo/
├── main.js                    # Electron entry point
├── preload.js                 # Electron preload script
├── server.py                  # Python entry point (3 lines)
├── server/                    # Flask backend
│   ├── __init__.py            # App factory, blueprint registration
│   ├── config.py              # Constants: port, paths, extensions
│   ├── state.py               # Thread-safe download progress
│   └── routes/                # API endpoints (one file per domain)
│       ├── profiles.py        # Profile CRUD
│       ├── downloads.py       # YouTube download management
│       ├── library.py         # File browsing, streaming
│       ├── playlists.py       # Playlist management
│       ├── stats.py           # Play tracking, achievements
│       └── mobile.py          # Mobile HTML/download endpoints
├── ui/                        # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── App.vue            # Main orchestrator (audio player logic)
│   │   ├── config.js          # Server URL resolution
│   │   ├── main.js            # Vue app bootstrap + theme imports
│   │   ├── components/        # One component per feature
│   │   ├── services/          # API client modules
│   │   └── assets/
│   │       ├── styles/        # base.css + theme-*.css
│   │       └── js/            # Theme animation scripts
│   └── vite.config.js         # Dev proxy → localhost:5001
├── static/                    # Standalone HTML (served to phones)
│   ├── mobile.html            # Self-contained mobile interface
│   ├── qr.html                # QR code generator
│   └── sw.js                  # Service worker for mobile PWA
├── docs/                      # Project documentation
│   ├── architecture.md        # Architecture, runtime flow, API reference
│   ├── changelog.md           # Version history
│   ├── roadmap.md             # Feature backlog and tech debt
│   ├── features/              # Feature-specific documentation
│   └── guides/                # Development and testing guides
├── build/                     # Packaging assets (icons, backgrounds)
├── .github/workflows/         # CI: multi-platform release builds
├── start.sh                   # Quick-start script
└── package.json               # Electron + build configuration
```

---

## Key Warnings for Agents

> [!CAUTION]
> **`index.html` in root is LEGACY.** It is a 28KB standalone prototype that is NOT the active frontend. The real frontend is in `ui/src/` and gets built to `ui/dist/`. Do not modify the root `index.html` unless explicitly asked.

> [!WARNING]
> **Audio streaming requires Flask running.** The Vue dev server proxies `/api/*` to Flask on port 5001. If Flask isn't running, all API calls and audio streaming will fail silently.

> [!WARNING]
> **`App.vue` is 666 lines.** It is the audio player orchestrator and handles playback, queue, shuffle, equalizer, and theme state. Be careful with changes — many components depend on props/events from `App.vue`.

---

## Documentation Map

| Document | What's in it |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Runtime flow, project structure, API reference, design decisions |
| [`docs/changelog.md`](docs/changelog.md) | Version history and what changed |
| [`docs/roadmap.md`](docs/roadmap.md) | Planned features, tech debt backlog |
| [`docs/guides/development.md`](docs/guides/development.md) | Full development setup guide |
| [`docs/guides/testing.md`](docs/guides/testing.md) | Manual testing checklist |
| [`docs/features/profiles.md`](docs/features/profiles.md) | Multi-profile system documentation |
| [`docs/features/karaoke-theme.md`](docs/features/karaoke-theme.md) | Karaoke mode architecture |
| [`docs/features/mobile-access.md`](docs/features/mobile-access.md) | Mobile interface and network setup |
| [`ui/src/assets/styles/THEME_GUIDE.md`](ui/src/assets/styles/THEME_GUIDE.md) | CSS theme creation rules |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Quick reference for contributors |
