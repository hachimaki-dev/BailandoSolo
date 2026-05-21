"""
Bailando Solo — Download routes.
Handles YouTube analysis, download initiation, and progress tracking.
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
    if d['status'] == 'downloading':
        video_id = d.get('info_dict', {}).get('id', 'unknown')

        # Calculate percentage
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)

        if total_bytes:
            percent = (downloaded_bytes / total_bytes) * 100
        else:
            percent = 0

        update_download_status(video_id, {
            'status': 'downloading',
            'percent': percent,
            'filename': d.get('filename', 'unknown'),
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0)
        })
    elif d['status'] == 'finished':
        video_id = d.get('info_dict', {}).get('id', 'unknown')
        update_download_status(video_id, {
            'status': 'finished',
            'percent': 100,
            'filename': d.get('filename', 'unknown')
        })


def _download_thread(url, folder_name, selected_ids):
    """Background thread to handle the download process."""
    # Get active profile
    config = load_profiles()
    active_profile = config.get('active', 'Default')

    # Create directory if it doesn't exist
    base_dir = os.path.join(DOWNLOADS_DIR, active_profile, folder_name)
    os.makedirs(base_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(base_dir, '%(title)s.%(ext)s'),
        'writethumbnail': True,
        'progress_hooks': [_progress_hook],
        'ignoreerrors': True,
    }

    urls_to_download = []
    if 'list=' in url and not selected_ids:
        urls_to_download = [url]  # Download whole playlist
    elif selected_ids:
        # Construct video URLs from IDs
        urls_to_download = [f"https://www.youtube.com/watch?v={vid}" for vid in selected_ids]
    else:
        urls_to_download = [url]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls_to_download)
    except Exception as e:
        print(f"Download error: {e}")


# ─── Routes ───────────────────────────────────────────────────────────────────

@downloads_bp.route('/api/analyze', methods=['POST'])
def analyze_playlist():
    """Analyze a YouTube URL and return song/playlist metadata."""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ydl_opts = {
        'extract_flat': True,
        'dump_single_json': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Handle both single video and playlist
            if 'entries' in info:
                entries = info['entries']
                title = info.get('title', 'Playlist')
            else:
                entries = [info]
                title = info.get('title', 'Video')

            # Clean up entries
            songs = []
            for entry in entries:
                if entry:  # entry can be None if video is deleted
                    songs.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'uploader': entry.get('uploader'),
                        'duration': entry.get('duration'),
                        'thumbnail': entry.get('thumbnails')[-1]['url'] if entry.get('thumbnails') else None
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
    """Start downloading songs in a background thread."""
    data = request.json
    url = data.get('url')
    folder_name = data.get('folder_name', 'Music')
    selected_ids = data.get('selected_ids', [])

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Start download in a separate thread
    thread = threading.Thread(target=_download_thread, args=(url, folder_name, selected_ids))
    thread.start()

    return jsonify({'status': 'started', 'message': 'Download started in background'})


@downloads_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get current download progress for all active downloads."""
    return jsonify(get_download_status())
