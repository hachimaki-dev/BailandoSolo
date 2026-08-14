"""
Bailando Solo — Library routes.
Handles browsing folders, listing songs, streaming audio/images, searching, metadata editing and random songs.
"""

import os
import re
import random
import glob
from urllib.parse import quote

from flask import Blueprint, jsonify, request, send_file

from server.config import DOWNLOADS_DIR, AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, UI_DIST_DIR
from server.routes.profiles import load_profiles

library_bp = Blueprint('library', __name__)


def _get_profile_dir():
    """Get the active profile's downloads directory."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')
    return os.path.join(DOWNLOADS_DIR, active_profile)


def _clean_title_and_artist(base_name):
    """
    Heuristically extract artist and title from filename if separated by ' - '.
    Example: 'Queen - Bohemian Rhapsody' -> artist='Queen', title='Bohemian Rhapsody'
    """
    if ' - ' in base_name:
        parts = base_name.split(' - ', 1)
        artist = parts[0].strip()
        title = parts[1].strip()
        return artist, title
    return None, base_name


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

        # Count songs in folder
        song_count = 0
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if any(f.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
                    song_count += 1

        folders_data.append({
            'name': folder,
            'thumbnail': thumbnail,
            'song_count': song_count
        })

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
            artist, title = _clean_title_and_artist(base_name)
            
            # File metadata
            stat = os.stat(filepath)
            file_size = stat.st_size
            mtime = stat.st_mtime

            thumbnail = None
            for thumb_ext in ['.jpg', '.png', '.webp', '.jpeg']:
                thumb_path = os.path.join(folder_path, base_name + thumb_ext)
                if os.path.exists(thumb_path):
                    thumbnail = f"/api/stream/{quote(folder)}/{quote(base_name + thumb_ext)}"
                    break

            files.append({
                'filename': filename,
                'path': f"/api/stream/{quote(folder)}/{quote(filename)}",
                'thumbnail': thumbnail,
                'title': title,
                'uploader': artist or 'Desconocido',
                'folder': folder,
                'size': file_size,
                'mtime': mtime,
                'ext': ext.replace('.', '').upper()
            })

    return jsonify(files)


@library_bp.route('/api/library/all', methods=['GET'])
def get_all_library_songs():
    """List all audio files across all folders in the active profile with rich metadata."""
    base_dir = _get_profile_dir()

    if not os.path.exists(base_dir):
        return jsonify([])

    all_songs = []
    for root, dirs, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            continue
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in AUDIO_EXTENSIONS:
                filepath = os.path.join(root, filename)
                base_name = os.path.splitext(filename)[0]
                artist, title = _clean_title_and_artist(base_name)
                
                stat = os.stat(filepath)
                file_size = stat.st_size
                mtime = stat.st_mtime

                thumbnail = None
                for thumb_ext in ['.jpg', '.png', '.webp', '.jpeg']:
                    thumb_path = os.path.join(root, base_name + thumb_ext)
                    if os.path.exists(thumb_path):
                        thumbnail = f"/api/stream/{quote(rel_path)}/{quote(base_name + thumb_ext)}"
                        break

                all_songs.append({
                    'filename': filename,
                    'path': f"/api/stream/{quote(rel_path)}/{quote(filename)}",
                    'thumbnail': thumbnail,
                    'title': title,
                    'uploader': artist or 'Desconocido',
                    'folder': rel_path,
                    'size': file_size,
                    'mtime': mtime,
                    'ext': ext.replace('.', '').upper()
                })

    return jsonify(all_songs)


@library_bp.route('/api/library/check-duplicates', methods=['POST'])
def check_duplicates():
    """
    Check a list of song titles or IDs against existing library files.
    Returns matching files found.
    """
    data = request.json or {}
    items = data.get('items', [])  # list of { id, title, uploader }

    base_dir = _get_profile_dir()
    if not os.path.exists(base_dir):
        return jsonify({'duplicates': []})

    # Collect normalized existing filenames and titles
    existing_songs = []
    for root, dirs, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            continue
        for filename in files:
            if any(filename.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
                base_name = os.path.splitext(filename)[0]
                existing_songs.append({
                    'filename': filename,
                    'base_name': base_name,
                    'norm': re.sub(r'[^a-zA-Z0-9]', '', base_name).lower(),
                    'folder': rel_path
                })

    duplicates = []
    for item in items:
        item_id = item.get('id')
        item_title = item.get('title', '')
        norm_title = re.sub(r'[^a-zA-Z0-9]', '', item_title).lower()

        match = None
        for ex in existing_songs:
            if norm_title and norm_title in ex['norm'] or ex['norm'] in norm_title:
                match = ex
                break

        if match:
            duplicates.append({
                'id': item_id,
                'title': item_title,
                'existing_filename': match['filename'],
                'existing_folder': match['folder']
            })

    return jsonify({'duplicates': duplicates})


@library_bp.route('/api/library/edit-metadata', methods=['POST'])
def edit_metadata():
    """
    Edit song metadata by renaming the audio file and its matching cover image.
    """
    data = request.json or {}
    folder = data.get('folder')
    old_filename = data.get('old_filename')
    new_title = data.get('title', '').strip()
    new_artist = data.get('artist', '').strip()
    target_folder = data.get('new_folder') or folder

    if not folder or not old_filename or not new_title:
        return jsonify({'error': 'Missing required fields'}), 400

    base_dir = _get_profile_dir()
    src_folder_path = os.path.join(base_dir, folder)
    src_file_path = os.path.join(src_folder_path, old_filename)

    if not os.path.exists(src_file_path):
        return jsonify({'error': 'Original file not found'}), 404

    ext = os.path.splitext(old_filename)[1]
    old_base_name = os.path.splitext(old_filename)[0]

    # Construct new base filename
    if new_artist and new_artist.lower() != 'desconocido':
        new_base_name = f"{new_artist} - {new_title}"
    else:
        new_base_name = new_title

    # Sanitize filename
    new_base_name = re.sub(r'[\\/*?:"<>|]', '_', new_base_name)
    new_filename = new_base_name + ext

    dst_folder_path = os.path.join(base_dir, target_folder)
    os.makedirs(dst_folder_path, exist_ok=True)
    dst_file_path = os.path.join(dst_folder_path, new_filename)

    try:
        # Rename audio file
        os.rename(src_file_path, dst_file_path)

        # Rename companion thumbnail if it exists
        for thumb_ext in ['.jpg', '.png', '.webp', '.jpeg']:
            old_thumb = os.path.join(src_folder_path, old_base_name + thumb_ext)
            new_thumb = os.path.join(dst_folder_path, new_base_name + thumb_ext)
            if os.path.exists(old_thumb):
                os.rename(old_thumb, new_thumb)
                break

        return jsonify({
            'status': 'success',
            'filename': new_filename,
            'folder': target_folder,
            'title': new_title,
            'artist': new_artist,
            'path': f"/api/stream/{quote(target_folder)}/{quote(new_filename)}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@library_bp.route('/api/library/delete-song', methods=['POST'])
def delete_song():
    """
    Delete a song and its companion thumbnail from the library.
    """
    data = request.json or {}
    folder = data.get('folder')
    filename = data.get('filename')

    if not folder or not filename:
        return jsonify({'error': 'Folder and filename are required'}), 400

    base_dir = _get_profile_dir()
    folder_path = os.path.join(base_dir, folder)
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    base_name = os.path.splitext(filename)[0]

    try:
        os.remove(file_path)
        for thumb_ext in ['.jpg', '.png', '.webp', '.jpeg']:
            thumb = os.path.join(folder_path, base_name + thumb_ext)
            if os.path.exists(thumb):
                os.remove(thumb)
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
            if any(filename.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
                base_name = os.path.splitext(filename)[0]
                artist, title = _clean_title_and_artist(base_name)
                thumbnail = None
                for thumb_ext in ['.jpg', '.png', '.webp', '.jpeg']:
                    thumb_path = os.path.join(root, base_name + thumb_ext)
                    if os.path.exists(thumb_path):
                        thumbnail = f"/api/stream/{quote(rel_path)}/{quote(base_name + thumb_ext)}"
                        break
                all_songs.append({
                    'filename': filename,
                    'path': f"/api/stream/{quote(rel_path)}/{quote(filename)}",
                    'thumbnail': thumbnail,
                    'title': title,
                    'uploader': artist or 'Desconocido',
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
