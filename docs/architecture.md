# Bailando Solo — Architecture

## Overview

Bailando Solo is a personal music downloader and player with a retro gaming aesthetic. It combines:

- **Python Flask backend** — Downloads music from YouTube via yt-dlp, manages profiles and stats
- **Vue 3 desktop frontend** — Rich audio player with themes, equalizer, visualizer, karaoke mode
- **Standalone mobile web interface** — Lightweight HTML page for browsing/downloading from phones
- **Electron wrapper** — Optional desktop app packaging

## Runtime Flow

```
┌──────────────┐     spawns      ┌─────────────────┐
│   Electron   │ ──────────────► │  Python (Flask)  │
│   main.js    │                 │  server.py       │
└──────┬───────┘                 └────────┬─────────┘
       │ loads                            │ serves API
       ▼                                  ▼
┌──────────────┐    HTTP /api/*   ┌───────────────┐
│   Vue UI     │ ◄──────────────► │  JSON REST API │
│  (ui/dist)   │                  └───────┬───────┘
└──────────────┘                          │ reads/writes
                                          ▼
                                  ┌───────────────┐
                                  │  File System   │
                                  │  downloads/    │
                                  │  profiles.json │
                                  │  stats.json    │
                                  └───────────────┘
```

## Project Structure

```
BailandoSolo/
├── server.py                  # Entry point (3 lines — imports and runs)
├── server/                    # Flask backend package
│   ├── __init__.py            # App factory — creates Flask app, registers blueprints
│   ├── config.py              # All constants: port, paths, extensions
│   ├── state.py               # Thread-safe download progress tracking
│   └── routes/
│       ├── profiles.py        # Profile CRUD + helpers (load/save/ensure)
│       ├── downloads.py       # YouTube analysis, download threads, progress
│       ├── library.py         # Browse folders, list songs, stream files, serve UI
│       ├── stats.py           # Play tracking, achievement calculations
│       └── mobile.py          # Mobile HTML pages, file/folder downloads
├── ui/                        # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── App.vue            # Main app — audio player orchestration
│   │   ├── components/        # Vue components (one per feature)
│   │   ├── services/          # API client modules
│   │   └── assets/
│   │       ├── styles/        # CSS: base.css + theme-*.css files
│   │       └── js/            # Theme animation scripts
│   └── vite.config.js         # Dev proxy → localhost:5001
├── static/                    # Standalone HTML pages
│   ├── mobile.html            # Mobile interface (self-contained)
│   ├── test-mobile.html       # Mobile connectivity test
│   └── qr.html                # QR code generator
├── main.js                    # Electron entry point
├── start.sh                   # Quick-start script (venv + deps + server)
├── downloads/                 # Music library (per-profile subdirectories)
├── profiles.json              # Profile configuration
└── stats.json                 # Play statistics
```

## Key Design Decisions

### Why Flask Blueprints (not separate services)
The backend is ~800 lines total. Splitting into microservices would add deployment complexity for zero benefit. Blueprints give us file-level separation with zero overhead.

### Why standalone mobile.html (not Vue)
The mobile interface is served to phones on the local network. A self-contained HTML file with inline CSS/JS means no build step, no asset resolution issues, and instant loading on any device.

### Why thread-safe dict (not a task queue)
This is a personal app running 1-2 concurrent downloads. A `threading.Lock` around a dict is sufficient. Celery/Redis would be absurd overkill.

### Why no DTOs or type system
The API returns plain dicts, the frontend consumes plain JSON. Adding a Python dataclass layer would double the maintenance surface with no consumer benefit.

## How to Run

### Quick start (standalone)
```bash
./start.sh
# Opens at http://localhost:5001
```

### Development mode (with hot-reload)
```bash
# Terminal 1: Python backend
source venv/bin/activate
python3 server.py

# Terminal 2: Vue dev server
cd ui && npm run dev
# Opens at http://localhost:5173 (proxies API to :5001)
```

### Electron desktop app
```bash
npm run dev    # Dev mode with hot-reload
npm run start  # Production build
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create profile `{name}` |
| DELETE | `/api/profiles/<name>` | Delete profile |
| POST | `/api/profiles/<name>/rename` | Rename profile `{new_name}` |
| POST | `/api/profiles/active` | Set active profile `{profile}` |
| POST | `/api/analyze` | Analyze YouTube URL `{url}` |
| POST | `/api/download` | Start download `{url, folder_name, selected_ids}` |
| GET | `/api/status` | Download progress |
| GET | `/api/library` | List folders in active profile |
| GET | `/api/library/<folder>` | List songs in folder |
| GET | `/api/library/random` | 20 random songs |
| GET | `/api/stream/<path>` | Stream audio/image file |
| POST | `/api/stats/track` | Record play event `{type, song_id}` |
| GET | `/api/stats` | Get all statistics |
| GET | `/api/mobile/info` | Network info for mobile |
| GET | `/api/mobile/download/<path>` | Force-download a file |
| GET | `/api/mobile/download-folder/<folder>` | Download folder as ZIP |
| POST | `/api/mobile/quick-download` | Remote YouTube download to PC `{query, folder}` |
| GET | `/api/mobile/quick-status/<task_id>` | Status/progress of remote mobile download |
| GET | `/api/tunnel/status` | Current status of Cloudflare/Localtunnel HTTPS tunnel |
| POST | `/api/tunnel/start` | Start HTTPS tunnel to bypass AP isolation/firewall |
| POST | `/api/tunnel/stop` | Stop running HTTPS tunnel |

## Configuration

Port and paths are centralized in `server/config.py`. Override the port via environment variable:

```bash
BAILANDO_PORT=8080 python3 server.py
```
