"""
Bailando Solo — Download routes.
Handles YouTube analysis, download initiation, progress tracking and duplicate handling,
with resilient networking options for restrictive environments (university networks/AP isolation/firewalls).
"""

import os
import shutil
import threading

from flask import Blueprint, request, jsonify
import yt_dlp

from server.config import DOWNLOADS_DIR
from server.state import get_download_status, update_download_status
from server.routes.profiles import load_profiles

downloads_bp = Blueprint('downloads', __name__)


# ─── Resilient Options Builder ────────────────────────────────────────────────

def _build_ydl_options(base_opts=None, cookies_browser=None, proxy=None):
    """
    Construct yt-dlp configuration with maximum resilience against
    restrictive networks (IPv4 forcing, Node JS runtime, aggressive retries).
    """
    opts = {
        # Force IPv4 (essential for avoiding broken IPv6 drops on campus/Eduroam networks)
        'source_address': '0.0.0.0',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb', 'android', 'ios']
            }
        },
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 5,
        'buffersize': 1024 * 16,
        'http_chunk_size': 10485760,  # 10 MB chunks
        'quiet': False,
        'no_warnings': False,
    }

    # Pass Node JS runtime if available on the system (solves n-challenge and signature deciphering)
    node_path = shutil.which('node') or '/opt/homebrew/bin/node' or '/usr/local/bin/node'
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

def _progress_hook(d):
    """Callback hook for yt-dlp to update download progress."""
    info = d.get('info_dict') or {}
    video_id = info.get('id', 'unknown')

    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)

        if total_bytes > 0:
            percent = (downloaded_bytes / total_bytes) * 100
        else:
            percent = 0

        update_download_status(video_id, {
            'status': 'downloading',
            'percent': round(percent, 1),
            'filename': os.path.basename(d.get('filename', 'unknown')),
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0),
            'downloaded_bytes': downloaded_bytes,
            'total_bytes': total_bytes
        })
    elif d['status'] == 'finished':
        update_download_status(video_id, {
            'status': 'finished',
            'percent': 100,
            'filename': os.path.basename(d.get('filename', 'unknown')),
            'speed': 0,
            'eta': 0
        })
    elif d['status'] == 'error':
        update_download_status(video_id, {
            'status': 'error',
            'percent': 0,
            'error': str(d.get('error', 'Error desconocido'))
        })


def _download_thread(url, folder_name, selected_ids, quality='192', naming_template='default', cookies_browser=None, proxy=None):
    """Background thread to handle the download process with custom options and item-level error handling."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')

    base_dir = os.path.join(DOWNLOADS_DIR, active_profile, folder_name)
    os.makedirs(base_dir, exist_ok=True)

    # Template output
    if naming_template == 'artist_title':
        outtmpl = os.path.join(base_dir, '%(artist,uploader)s - %(title)s.%(ext)s')
    else:
        outtmpl = os.path.join(base_dir, '%(title)s.%(ext)s')

    base_ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': str(quality),
        }],
        'outtmpl': outtmpl,
        'writethumbnail': True,
        'progress_hooks': [_progress_hook],
        'ignoreerrors': False,
    }

    ydl_opts = _build_ydl_options(base_ydl_opts, cookies_browser=cookies_browser, proxy=proxy)

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
        update_download_status(sid, {
            'status': 'downloading',
            'percent': 0,
            'speed': 0,
            'eta': 0
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([target_url])

            current_status = get_download_status().get(sid, {})
            if current_status.get('status') != 'error':
                update_download_status(sid, {
                    'status': 'finished',
                    'percent': 100,
                    'speed': 0,
                    'eta': 0
                })
        except Exception as e:
            err_msg = str(e)
            print(f"Error downloading {sid} from {target_url}: {err_msg}")
            
            # Surface helpful suggestions if rate limit or bot check detected
            if any(k in err_msg.lower() for k in ['bot', 'sign in', 'confirm', '429']):
                err_msg = "Bloqueado por YouTube (detección de bot en IP compartida). Activa 'Sesión de Navegador' en opciones de Red para continuar."
            
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
        args=(url, folder_name, selected_ids, quality, naming_template, cookies_browser, proxy)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started', 'message': 'Download started in background'})


@downloads_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get current download progress for all active downloads."""
    return jsonify(get_download_status())
