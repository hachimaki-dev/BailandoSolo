"""
Bailando Solo — Download routes.
Handles YouTube analysis, download initiation, progress tracking and duplicate handling,
with resilient networking options for restrictive environments (university networks/AP isolation/firewalls).
"""

import sys
import os
import re
import json
import shutil
import threading
import urllib.request

from flask import Blueprint, request, jsonify
import yt_dlp

from server.config import DOWNLOADS_DIR
from server.state import get_download_status, update_download_status
from server.routes.profiles import load_profiles

downloads_bp = Blueprint('downloads', __name__)


# ─── FFmpeg Locator ────────────────────────────────────────────────────────────

def _find_ffmpeg():
    """Find ffmpeg binary in bundled application resources or system PATH."""
    candidates = []

    # Check bundled paths (PyInstaller / Electron Resources)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.extend([
            os.path.join(exe_dir, 'ffmpeg.exe'),
            os.path.join(exe_dir, 'ffmpeg'),
            os.path.join(getattr(sys, '_MEIPASS', ''), 'ffmpeg.exe'),
            os.path.join(getattr(sys, '_MEIPASS', ''), 'ffmpeg'),
        ])

    # Project dist / resources fallback
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates.extend([
        os.path.join(project_root, 'dist', 'ffmpeg.exe'),
        os.path.join(project_root, 'dist', 'ffmpeg'),
    ])

    # System PATH and standard OS binaries
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        candidates.append(system_ffmpeg)

    candidates.extend([
        '/opt/homebrew/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
        '/usr/bin/ffmpeg',
        r'C:\ProgramData\chocolatey\bin\ffmpeg.exe'
    ])

    for c in candidates:
        if c and os.path.isfile(c):
            if os.name != 'nt' and not os.access(c, os.X_OK):
                try:
                    os.chmod(c, 0o755)
                except Exception:
                    pass
            return c
    return None


# ─── Resilient Options Builder ────────────────────────────────────────────────

def _build_ydl_options(base_opts=None, cookies_browser=None, proxy=None):
    """
    Construct yt-dlp configuration with maximum resilience against
    restrictive networks (IPv4 forcing, SSL certificate bypass for campus firewalls,
    Node JS signature solver, browser cookies, and aggressive retries).
    """
    opts = {
        # Force IPv4 (essential for avoiding broken IPv6 drops on campus/Eduroam networks)
        'source_address': '0.0.0.0',
        # Ignore SSL certificate verification issues (essential for campus firewalls with MITM/self-signed certs)
        'nocheckcertificate': True,
        'geo_bypass': True,
        'remote_components': ['ejs:github'],
        'socket_timeout': 35,
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 5,
        'buffersize': 1024 * 16,
        'http_chunk_size': 10485760,  # 10 MB chunks
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-419,es;q=0.9,en;q=0.8',
        }
    }

    # Pass Node JS runtime if available on the system (solves n-challenge and signature deciphering)
    node_path = shutil.which('node') or ('/opt/homebrew/bin/node' if os.path.exists('/opt/homebrew/bin/node') else None) or ('/usr/local/bin/node' if os.path.exists('/usr/local/bin/node') else None)
    if node_path and os.path.exists(node_path):
        opts['js_runtimes'] = {'node': {'path': node_path}}

    # Browser session cookies (bypasses bot detection & HTTP 429 on shared campus IPs)
    if cookies_browser and cookies_browser.lower() not in ('none', 'false', '', 'null', 'desactivado'):
        opts['cookiesfrombrowser'] = (cookies_browser.lower(),)

    # Optional HTTP/SOCKS5 proxy
    if proxy and proxy.strip():
        opts['proxy'] = proxy.strip()

    if base_opts:
        opts.update(base_opts)

    return opts


# ─── Download helpers ─────────────────────────────────────────────────────────

# ─── Download helpers ─────────────────────────────────────────────────────────

def _create_progress_hook(target_id):
    """
    Create a progress hook closure that reliably updates the given target song ID
    with real-time percentage, transfer speed, and human-readable stages.
    """
    def hook(d):
        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                raw_pct = (downloaded / total) * 100.0
            else:
                raw_pct = 0.0

            # Scale to 90% during audio stream download, leaving 90-100% for FFmpeg conversion
            scaled_pct = min(90.0, round(raw_pct * 0.9, 1))
            display_pct = max(scaled_pct, 5.0)

            update_download_status(target_id, {
                'status': 'downloading',
                'stage': 'Descargando audio...',
                'percent': display_pct,
                'downloaded_bytes': downloaded,
                'total_bytes': total,
                'speed': d.get('speed') or 0,
                'eta': d.get('eta') or 0,
                'filename': os.path.basename(d.get('filename') or 'audio.mp3')
            })
        elif status == 'finished':
            # Finished raw download, now converting with FFmpeg
            update_download_status(target_id, {
                'status': 'processing',
                'stage': 'Extrayendo audio a MP3...',
                'percent': 95.0,
                'speed': 0,
                'eta': 0
            })
    return hook


def _download_thread(url, folder_name, selected_ids, quality='192', naming_template='default', cookies_browser=None, proxy=None, songs_info=None):
    """Background thread to handle the download process with smart search fallback for unavailable/geo-blocked videos."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')

    base_dir = os.path.join(DOWNLOADS_DIR, active_profile, folder_name)
    os.makedirs(base_dir, exist_ok=True)

    # Template output
    if naming_template == 'artist_title':
        outtmpl = os.path.join(base_dir, '%(artist,uploader)s - %(title)s.%(ext)s')
    else:
        outtmpl = os.path.join(base_dir, '%(title)s.%(ext)s')

    ffmpeg_bin = _find_ffmpeg()
    postprocessors = []
    if ffmpeg_bin:
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': str(quality),
        })
    else:
        print("[Audio Engine] ffmpeg no detectado en el sistema ni en recursos. Descargando pista de audio directa (bestaudio)...")

    base_ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': postprocessors,
        'outtmpl': outtmpl,
        'writethumbnail': True,
        'ignoreerrors': False,
    }
    if ffmpeg_bin:
        base_ydl_opts['ffmpeg_location'] = ffmpeg_bin

    ydl_opts = _build_ydl_options(base_ydl_opts, cookies_browser=cookies_browser, proxy=proxy)

    # Map metadata for fallback
    meta_map = {}
    if songs_info and isinstance(songs_info, list):
        for s in songs_info:
            if s and s.get('id'):
                meta_map[s['id']] = {
                    'title': s.get('title') or '',
                    'uploader': s.get('uploader') or ''
                }

    # Prepare item list: download one by one so progress and errors are clearly tracked
    targets = []
    if selected_ids:
        for sid in selected_ids:
            targets.append((sid, f"https://www.youtube.com/watch?v={sid}"))
    elif 'list=' in url:
        targets.append(('playlist_batch', url))
    else:
        targets.append(('single_url', url))

    for sid, target_url in targets:
        hook = _create_progress_hook(sid)

        update_download_status(sid, {
            'status': 'downloading',
            'stage': 'Iniciando descarga...',
            'percent': 5.0,
            'speed': 0,
            'eta': 0
        })

        success = False
        last_error = ""

        # 1. Attempt direct download
        try:
            item_opts = dict(ydl_opts)
            item_opts['progress_hooks'] = [hook]
            with yt_dlp.YoutubeDL(item_opts) as ydl:
                ydl.download([target_url])

            current_status = get_download_status().get(sid, {})
            if current_status.get('status') != 'error':
                success = True
                update_download_status(sid, {
                    'status': 'finished',
                    'stage': 'Completado',
                    'percent': 100,
                    'speed': 0,
                    'eta': 0
                })
        except Exception as e:
            last_error = str(e)
            print(f"[Direct Download] {sid} failed ({last_error}). Checking smart fallback...")

        # 2. Smart Fallback Search: If direct download fails (e.g. video unavailable, geo-blocked Topic song)
        if not success:
            update_download_status(sid, {
                'status': 'searching',
                'stage': 'Buscando versión alternativa...',
                'percent': 12.0,
                'speed': 0,
                'eta': 0
            })

            meta = meta_map.get(sid, {})
            title = meta.get('title') or ''
            uploader = meta.get('uploader') or ''

            # If metadata not passed, attempt quick oembed lookup to discover title and uploader
            if not title and sid not in ('playlist_batch', 'single_url'):
                try:
                    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={sid}&format=json"
                    req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as o_resp:
                        o_data = json.loads(o_resp.read().decode('utf-8'))
                        title = o_data.get('title') or ''
                        uploader = o_data.get('author_name') or ''
                except Exception:
                    pass

            if title:
                print(f"[Smart Fallback] Direct video unavailable for {sid}. Searching alternative for '{title}' by '{uploader}'...")
                clean_uploader = re.sub(r' - Topic$', '', uploader).strip()
                search_queries = []
                if clean_uploader and clean_uploader.lower() not in title.lower():
                    search_queries.append(f"ytsearch3:{clean_uploader} {title}")
                search_queries.append(f"ytsearch3:{title}")

                clean_title = re.sub(r'[\\/*?:"<>|]', '', title).strip()
                if naming_template == 'artist_title' and clean_uploader:
                    clean_name = f"{clean_uploader} - {clean_title}"
                else:
                    clean_name = clean_title

                fallback_base = dict(ydl_opts)
                fallback_base['outtmpl'] = os.path.join(base_dir, f"{clean_name}.%(ext)s")
                fallback_base['progress_hooks'] = [hook]

                for query in search_queries:
                    if success:
                        break
                    try:
                        search_opts = _build_ydl_options({'extract_flat': True, 'quiet': True}, cookies_browser=cookies_browser, proxy=proxy)
                        with yt_dlp.YoutubeDL(search_opts) as s_ydl:
                            search_res = s_ydl.extract_info(query, download=False)
                            entries = search_res.get('entries', []) if search_res else []
                            for entry in entries:
                                cand_id = entry.get('id') if entry else None
                                if cand_id and cand_id != sid:
                                    print(f"[Smart Fallback] Trying candidate {cand_id}: {entry.get('title')}")
                                    try:
                                        with yt_dlp.YoutubeDL(fallback_base) as dl_ydl:
                                            dl_ydl.download([f"https://www.youtube.com/watch?v={cand_id}"])
                                        success = True
                                        update_download_status(sid, {
                                            'status': 'finished',
                                            'stage': 'Completado',
                                            'percent': 100,
                                            'speed': 0,
                                            'eta': 0
                                        })
                                        print(f"[Smart Fallback] SUCCESS! Downloaded alternative for {sid} via {cand_id}")
                                        break
                                    except Exception as cand_err:
                                        print(f"[Smart Fallback] Candidate {cand_id} failed: {cand_err}")
                    except Exception as s_err:
                        print(f"[Smart Fallback] Search query '{query}' failed: {s_err}")

        # 3. If both direct download and smart fallback failed
        if not success:
            err_msg = last_error or "Error desconocido"
            if any(k in err_msg.lower() for k in ['bot', 'sign in', 'confirm', '429']):
                err_msg = "Bloqueado por YouTube (detección de bot en IP compartida). Activa 'Sesión de Navegador' en opciones de Red para continuar."
            elif any(k in err_msg.lower() for k in ['not available', 'unavailable']):
                err_msg = "Video no disponible en YouTube y no se encontró versión alternativa."

            update_download_status(sid, {
                'status': 'error',
                'percent': 0,
                'error': err_msg
            })


# ─── Routes ───────────────────────────────────────────────────────────────────

@downloads_bp.route('/api/analyze', methods=['POST'])
def analyze_playlist():
    """Analyze a YouTube URL and return song/playlist metadata with resilience options."""
    data = request.json or {}
    url = data.get('url')
    cookies_browser = data.get('cookies_browser')
    proxy = data.get('proxy')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    base_ydl_opts = {
        'extract_flat': True,
        'dump_single_json': True,
    }
    ydl_opts = _build_ydl_options(base_ydl_opts, cookies_browser=cookies_browser, proxy=proxy)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                entries = info['entries']
                title = info.get('title', 'Playlist')
            else:
                entries = [info]
                title = info.get('title', 'Video')

            songs = []
            for entry in entries:
                if entry:
                    raw_title = entry.get('title') or 'Sin título'
                    uploader = entry.get('uploader') or 'Desconocido'
                    
                    thumbnail_url = None
                    if entry.get('thumbnails'):
                        thumbnail_url = entry.get('thumbnails')[-1].get('url')

                    songs.append({
                        'id': entry.get('id'),
                        'title': raw_title,
                        'uploader': uploader,
                        'duration': entry.get('duration'),
                        'thumbnail': thumbnail_url
                    })

            return jsonify({
                'title': title,
                'songs': songs,
                'count': len(songs)
            })
    except Exception as e:
        err_msg = str(e)
        if any(k in err_msg.lower() for k in ['bot', 'sign in', 'confirm', '429']):
            err_msg = "YouTube detectó tráfico inusual en esta red WiFi (error 429). Activa 'Sesión de Navegador' en las opciones de Red para saltar el bloqueo."
        return jsonify({'error': err_msg}), 500


@downloads_bp.route('/api/download', methods=['POST'])
def start_download():
    """Start downloading songs in a background thread with quality, template, and network options."""
    data = request.json or {}
    url = data.get('url')
    folder_name = data.get('folder_name', 'Music')
    selected_ids = data.get('selected_ids', [])
    songs_info = data.get('songs_info', [])
    quality = data.get('quality', '192')
    naming_template = data.get('naming_template', 'default')
    cookies_browser = data.get('cookies_browser')
    proxy = data.get('proxy')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Mark selected IDs as waiting in state immediately
    for sid in selected_ids:
        update_download_status(sid, {
            'status': 'waiting',
            'percent': 0,
            'speed': 0,
            'eta': 0
        })

    # Start download in background thread
    thread = threading.Thread(
        target=_download_thread,
        args=(url, folder_name, selected_ids, quality, naming_template, cookies_browser, proxy, songs_info)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started', 'message': 'Download started in background'})


@downloads_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get current download progress for all active downloads."""
    return jsonify(get_download_status())
