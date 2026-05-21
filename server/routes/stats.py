"""
Bailando Solo — Statistics routes.
Handles play tracking and stats dashboard data.
"""

import os
import json
import time

from flask import Blueprint, request, jsonify

from server.config import STATS_FILE, DOWNLOADS_DIR, AUDIO_EXTENSIONS
from server.routes.profiles import load_profiles

stats_bp = Blueprint('stats', __name__)


def load_stats():
    """Load stats from JSON file."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_stats(stats):
    """Save stats to JSON file."""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")


@stats_bp.route('/api/stats/track', methods=['POST'])
def track_stat():
    """Record a play or time_update event."""
    data = request.json
    event_type = data.get('type')
    song_id = data.get('song_id')
    duration = data.get('duration', 0)

    if not song_id:
        return jsonify({'error': 'Song ID required'}), 400

    stats = load_stats()

    if song_id not in stats:
        stats[song_id] = {
            'play_count': 0,
            'total_time': 0,
            'last_played': None,
            'title': data.get('title', song_id)
        }

    if event_type == 'play':
        stats[song_id]['play_count'] += 1
        stats[song_id]['last_played'] = time.time()
    elif event_type == 'time_update':
        stats[song_id]['total_time'] += duration

    save_stats(stats)
    return jsonify({'status': 'ok'})


@stats_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive listening statistics and achievements."""
    stats = load_stats()

    empty_response = {
        'most_played': None, 'most_time': None, 'least_played': None,
        'never_played': [], 'total_plays': 0, 'total_time_global': 0,
        'top_folders': [], 'achievements': [], 'first_played': None,
        'last_played': None, 'library_explored_percent': 0,
        'unique_songs_played': 0, 'total_songs': 0
    }

    if not stats:
        return jsonify(empty_response)

    # Convert dict to list for sorting
    songs_list = []
    for sid, data in stats.items():
        data['id'] = sid
        songs_list.append(data)

    # Most/least played
    songs_list.sort(key=lambda x: x['play_count'], reverse=True)
    most_played = songs_list[0] if songs_list else None

    songs_list.sort(key=lambda x: x['total_time'], reverse=True)
    most_time = songs_list[0] if songs_list else None

    songs_list.sort(key=lambda x: x['play_count'])
    least_played = songs_list[0] if songs_list else None

    # First and Last played
    songs_with_time = [s for s in songs_list if s.get('last_played')]
    if songs_with_time:
        songs_with_time.sort(key=lambda x: x['last_played'])
        first_played = songs_with_time[0]
        last_played = songs_with_time[-1]
    else:
        first_played = None
        last_played = None

    # Scan library for never-played songs and folder stats
    config = load_profiles()
    active_profile = config.get('active', 'Default')
    base_dir = os.path.join(DOWNLOADS_DIR, active_profile)
    all_files = []
    folder_stats = {}

    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            rel_path = os.path.relpath(root, base_dir)
            if rel_path == '.':
                continue
            for filename in files:
                if any(filename.endswith(ext) for ext in AUDIO_EXTENSIONS):
                    all_files.append(filename)
                    if rel_path not in folder_stats:
                        folder_stats[rel_path] = {
                            'name': rel_path, 'play_count': 0,
                            'total_time': 0, 'song_count': 0
                        }
                    folder_stats[rel_path]['song_count'] += 1
                    if filename in stats:
                        folder_stats[rel_path]['play_count'] += stats[filename]['play_count']
                        folder_stats[rel_path]['total_time'] += stats[filename]['total_time']

    never_played = [f for f in all_files if f not in stats]
    top_folders = sorted(folder_stats.values(), key=lambda x: x['play_count'], reverse=True)[:3]

    # Global totals
    total_plays = sum(s['play_count'] for s in songs_list)
    total_time_global = sum(s['total_time'] for s in songs_list)
    unique_songs_played = len(songs_list)
    total_songs = len(all_files)
    lib_pct = (unique_songs_played / total_songs * 100) if total_songs > 0 else 0

    # Achievements
    achievements = []
    if total_time_global >= 360000:
        achievements.append({'id': 'marathon', 'icon': '🏃', 'title': 'Maratonista', 'desc': '100+ horas'})
    elif total_time_global >= 36000:
        achievements.append({'id': 'listener', 'icon': '🎧', 'title': 'Oyente Dedicado', 'desc': '10+ horas'})

    if lib_pct >= 75:
        achievements.append({'id': 'explorer', 'icon': '🗺️', 'title': 'Explorador', 'desc': '75% biblioteca'})
    elif lib_pct >= 50:
        achievements.append({'id': 'adventurer', 'icon': '🧭', 'title': 'Aventurero', 'desc': '50% biblioteca'})

    if total_songs >= 100:
        achievements.append({'id': 'collector', 'icon': '💎', 'title': 'Coleccionista', 'desc': '100+ canciones'})
    elif total_songs >= 50:
        achievements.append({'id': 'enthusiast', 'icon': '⭐', 'title': 'Entusiasta', 'desc': '50+ canciones'})

    if total_plays >= 500:
        achievements.append({'id': 'addict', 'icon': '🔥', 'title': 'Adicto Musical', 'desc': '500+ plays'})
    elif total_plays >= 100:
        achievements.append({'id': 'fan', 'icon': '🎵', 'title': 'Super Fan', 'desc': '100+ plays'})

    return jsonify({
        'most_played': most_played, 'most_time': most_time,
        'least_played': least_played, 'never_played': never_played[:50],
        'total_plays': total_plays, 'total_time_global': total_time_global,
        'top_folders': top_folders, 'achievements': achievements,
        'first_played': first_played, 'last_played': last_played,
        'library_explored_percent': round(lib_pct, 1),
        'unique_songs_played': unique_songs_played, 'total_songs': total_songs
    })
