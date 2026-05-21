"""
Bailando Solo — Library routes.
Handles browsing folders, listing songs, streaming audio/images, and random songs.
"""

import os
import random
import glob
from urllib.parse import quote

from flask import Blueprint, jsonify, send_file

from server.config import DOWNLOADS_DIR, AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, UI_DIST_DIR
from server.routes.profiles import load_profiles

library_bp = Blueprint('library', __name__)


def _get_profile_dir():
    """Get the active profile's downloads directory."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')
    return os.path.join(DOWNLOADS_DIR, active_profile)


@library_bp.route('/api/library', methods=['GET'])
def get_library():
    """List all folders in the active profile's directory with a random thumbnail."""
    base_dir = _get_profile_dir()

    if not os.path.exists(base_dir):
        return jsonify([])

    folders_data = []
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        thumbnail = None

        images = []
        for ext in IMAGE_EXTENSIONS:
            images.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
            images.extend(glob.glob(os.path.join(folder_path, f'*{ext.upper()}')))

        if images:
            selected_image = random.choice(images)
            filename = os.path.basename(selected_image)
            thumbnail = f"/api/stream/{quote(folder)}/{quote(filename)}"

        folders_data.append({'name': folder, 'thumbnail': thumbnail})

    return jsonify(folders_data)


@library_bp.route('/api/library/<folder>', methods=['GET'])
def get_folder_content(folder):
    """List all audio files in a specific folder within the active profile."""
    base_dir = _get_profile_dir()
    folder_path = os.path.join(base_dir, folder)

    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder not found'}), 404

    files = []
    for ext in AUDIO_EXTENSIONS:
        for filepath in glob.glob(os.path.join(folder_path, f'*{ext}')):
            filename = os.path.basename(filepath)
            base_name = os.path.splitext(filename)[0]
            thumbnail = None
            for thumb_ext in ['.jpg', '.png', '.webp']:
                thumb_path = os.path.join(folder_path, base_name + thumb_ext)
                if os.path.exists(thumb_path):
                    thumbnail = f"/api/stream/{folder}/{base_name}{thumb_ext}"
                    break
            files.append({
                'filename': filename,
                'path': f"/api/stream/{folder}/{filename}",
                'thumbnail': thumbnail,
                'title': base_name
            })

    return jsonify(files)


@library_bp.route('/api/stream/<path:filepath>', methods=['GET'])
def stream_file(filepath):
    """Serve a file from the active profile's directory."""
    base_dir = _get_profile_dir()
    safe_path = os.path.normpath(os.path.join(base_dir, filepath))
    if not safe_path.startswith(base_dir):
        return jsonify({'error': 'Access denied'}), 403
    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(safe_path)


@library_bp.route('/api/library/random', methods=['GET'])
def get_random_songs():
    """Get a random selection of songs from all folders in the active profile."""
    base_dir = _get_profile_dir()

    if not os.path.exists(base_dir):
        return jsonify([])

    all_songs = []
    for root, dirs, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            continue
        for filename in files:
            if any(filename.endswith(ext) for ext in AUDIO_EXTENSIONS):
                base_name = os.path.splitext(filename)[0]
                thumbnail = None
                for thumb_ext in ['.jpg', '.png', '.webp']:
                    thumb_path = os.path.join(root, base_name + thumb_ext)
                    if os.path.exists(thumb_path):
                        thumbnail = f"/api/stream/{rel_path}/{base_name}{thumb_ext}"
                        break
                all_songs.append({
                    'filename': filename,
                    'path': f"/api/stream/{rel_path}/{filename}",
                    'thumbnail': thumbnail,
                    'title': base_name,
                    'folder': rel_path
                })

    random.shuffle(all_songs)
    return jsonify(all_songs[:20])


@library_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets from the Vue build."""
    safe_path = os.path.normpath(os.path.join(UI_DIST_DIR, 'assets', filename))
    if not safe_path.startswith(os.path.join(UI_DIST_DIR, 'assets')):
        return jsonify({'error': 'Access denied'}), 403
    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(safe_path)


@library_bp.route('/')
def index():
    """Serve the main HTML file."""
    index_path = os.path.join(UI_DIST_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return "Error: ui/dist/index.html not found. Please build the UI first.", 404
