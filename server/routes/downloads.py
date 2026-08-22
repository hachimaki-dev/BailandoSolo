"""
Bailando Solo — Download routes.
Handles YouTube analysis, download initiation, progress tracking and duplicate handling.
"""

import os
import threading

from flask import Blueprint, request, jsonify
import yt_dlp

from server.config import DOWNLOADS_DIR
from server.state import get_download_status, update_download_status
from server.routes.profiles import load_profiles

downloads_bp = Blueprint('downloads', __name__)


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


def _download_thread(url, folder_name, selected_ids, quality='192', naming_template='default'):
    """Background thread to handle the download process with custom options."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')

    base_dir = os.path.join(DOWNLOADS_DIR, active_profile, folder_name)
    os.makedirs(base_dir, exist_ok=True)

    # Template output
    if naming_template == 'artist_title':
        outtmpl = os.path.join(base_dir, '%(artist,uploader)s - %(title)s.%(ext)s')
    else:
        outtmpl = os.path.join(base_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'web', 'android', 'ios']
            }
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': str(quality),
        }],
        'outtmpl': outtmpl,
        'writethumbnail': True,
        'progress_hooks': [_progress_hook],
        'ignoreerrors': True,
        'quiet': False,
        'no_warnings': False,
    }

    urls_to_download = []
    if 'list=' in url and not selected_ids:
        urls_to_download = [url]
    elif selected_ids:
        urls_to_download = [f"https://www.youtube.com/watch?v={vid}" for vid in selected_ids]
    else:
        urls_to_download = [url]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls_to_download)
    except Exception as e:
        print(f"Download thread error: {e}")
        for sid in (selected_ids or []):
            update_download_status(sid, {
                'status': 'error',
                'percent': 0,
                'error': str(e)
            })


# ─── Routes ───────────────────────────────────────────────────────────────────

@downloads_bp.route('/api/analyze', methods=['POST'])
def analyze_playlist():
    """Analyze a YouTube URL and return song/playlist metadata."""
    data = request.json or {}
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ydl_opts = {
        'extract_flat': True,
        'dump_single_json': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'web', 'android', 'ios']
            }
        },
    }

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
                    # Clean artist & title heuristic
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
        return jsonify({'error': str(e)}), 500


@downloads_bp.route('/api/download', methods=['POST'])
def start_download():
    """Start downloading songs in a background thread with quality and template options."""
    data = request.json or {}
    url = data.get('url')
    folder_name = data.get('folder_name', 'Music')
    selected_ids = data.get('selected_ids', [])
    quality = data.get('quality', '192')
    naming_template = data.get('naming_template', 'default')

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
        args=(url, folder_name, selected_ids, quality, naming_template)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started', 'message': 'Download started in background'})


@downloads_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get current download progress for all active downloads."""
    return jsonify(get_download_status())
