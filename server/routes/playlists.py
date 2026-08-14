"""
Bailando Solo — Playlists & Smart Crates routes.
Handles custom playlists, dynamic smart crates, and external synced playlists.
"""

import os
import json
import time
import uuid
from flask import Blueprint, request, jsonify

from server.config import PLAYLISTS_FILE
from server.routes.profiles import load_profiles

playlists_bp = Blueprint('playlists', __name__)


def _load_playlists_data():
    """Load all profiles' playlists from JSON file."""
    if os.path.exists(PLAYLISTS_FILE):
        try:
            with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_playlists_data(data):
    """Save playlists data to JSON file."""
    try:
        with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving playlists: {e}")


def _get_active_profile_playlists():
    """Get playlists for active profile, initializing defaults if needed."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')
    all_data = _load_playlists_data()
    
    if active_profile not in all_data:
        # Create default Smart Crates for new profiles
        all_data[active_profile] = [
            {
                'id': 'smart-top-spins',
                'name': '🔥 Más Escuchadas (Top 25)',
                'type': 'smart',
                'description': 'Tus 25 canciones con más reproducciones',
                'rule': { 'field': 'plays', 'operator': 'top', 'value': 25 },
                'created_at': time.time(),
                'songs': []
            },
            {
                'id': 'smart-recent-vault',
                'name': '✨ Agregadas Recientemente',
                'type': 'smart',
                'description': 'Canciones incorporadas en los últimos 30 días',
                'rule': { 'field': 'mtime', 'operator': 'days_ago', 'value': 30 },
                'created_at': time.time(),
                'songs': []
            },
            {
                'id': 'smart-unplayed',
                'name': '📦 Joyas de la Bóveda (0 Plays)',
                'type': 'smart',
                'description': 'Canciones de tu biblioteca que aún no has escuchado',
                'rule': { 'field': 'plays', 'operator': 'eq', 'value': 0 },
                'created_at': time.time(),
                'songs': []
            }
        ]
        _save_playlists_data(all_data)

    return active_profile, all_data[active_profile], all_data


@playlists_bp.route('/api/playlists', methods=['GET'])
def get_playlists():
    """Get all playlists and smart crates for the active profile."""
    _, profile_playlists, _ = _get_active_profile_playlists()
    return jsonify(profile_playlists)


@playlists_bp.route('/api/playlists', methods=['POST'])
def create_playlist():
    """Create a new custom playlist or smart crate."""
    data = request.json or {}
    name = data.get('name', '').strip()
    p_type = data.get('type', 'custom')  # 'custom', 'smart', 'synced'
    description = data.get('description', '')
    rule = data.get('rule', None)
    source_url = data.get('source_url', '')

    if not name:
        return jsonify({'error': 'El nombre de la playlist es obligatorio'}), 400

    active_profile, profile_playlists, all_data = _get_active_profile_playlists()

    new_pl = {
        'id': f"pl-{uuid.uuid4().hex[:10]}",
        'name': name,
        'type': p_type,
        'description': description,
        'rule': rule,
        'source_url': source_url,
        'created_at': time.time(),
        'updated_at': time.time(),
        'songs': data.get('songs', [])
    }

    profile_playlists.append(new_pl)
    all_data[active_profile] = profile_playlists
    _save_playlists_data(all_data)

    return jsonify(new_pl), 201


@playlists_bp.route('/api/playlists/<playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    """Update playlist properties or song list."""
    data = request.json or {}
    active_profile, profile_playlists, all_data = _get_active_profile_playlists()

    found = None
    for pl in profile_playlists:
        if pl['id'] == playlist_id:
            found = pl
            break

    if not found:
        return jsonify({'error': 'Playlist no encontrada'}), 404

    if 'name' in data and data['name'].strip():
        found['name'] = data['name'].strip()
    if 'description' in data:
        found['description'] = data['description']
    if 'songs' in data:
        found['songs'] = data['songs']
    if 'rule' in data:
        found['rule'] = data['rule']
    if 'source_url' in data:
        found['source_url'] = data['source_url']

    found['updated_at'] = time.time()
    all_data[active_profile] = profile_playlists
    _save_playlists_data(all_data)

    return jsonify(found)


@playlists_bp.route('/api/playlists/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """Delete a playlist."""
    active_profile, profile_playlists, all_data = _get_active_profile_playlists()

    all_data[active_profile] = [pl for pl in profile_playlists if pl['id'] != playlist_id]
    _save_playlists_data(all_data)

    return jsonify({'status': 'deleted'})


@playlists_bp.route('/api/playlists/<playlist_id>/add-song', methods=['POST'])
def add_song_to_playlist(playlist_id):
    """Add a song to a custom playlist."""
    data = request.json or {}
    song = data.get('song')

    if not song:
        return jsonify({'error': 'Canción requerida'}), 400

    active_profile, profile_playlists, all_data = _get_active_profile_playlists()

    found = None
    for pl in profile_playlists:
        if pl['id'] == playlist_id:
            found = pl
            break

    if not found:
        return jsonify({'error': 'Playlist no encontrada'}), 404

    if found.get('type') == 'smart':
        return jsonify({'error': 'Las Smart Crates se calculan dinámicamente'}), 400

    # Avoid duplicate additions if same path
    existing_paths = {s.get('path') for s in found.get('songs', [])}
    if song.get('path') not in existing_paths:
        found.setdefault('songs', []).append(song)
        found['updated_at'] = time.time()
        all_data[active_profile] = profile_playlists
        _save_playlists_data(all_data)

    return jsonify(found)


@playlists_bp.route('/api/playlists/<playlist_id>/remove-song', methods=['POST'])
def remove_song_from_playlist(playlist_id):
    """Remove a song from a playlist by path or index."""
    data = request.json or {}
    song_path = data.get('path')
    index = data.get('index')

    active_profile, profile_playlists, all_data = _get_active_profile_playlists()

    found = None
    for pl in profile_playlists:
        if pl['id'] == playlist_id:
            found = pl
            break

    if not found:
        return jsonify({'error': 'Playlist no encontrada'}), 404

    songs = found.get('songs', [])
    if index is not None and 0 <= index < len(songs):
        songs.pop(index)
    elif song_path:
        found['songs'] = [s for s in songs if s.get('path') != song_path]

    found['updated_at'] = time.time()
    all_data[active_profile] = profile_playlists
    _save_playlists_data(all_data)

    return jsonify(found)
