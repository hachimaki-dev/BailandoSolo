import os
import json
import threading
import socket
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import glob
from flask import send_file

app = Flask(__name__)
CORS(app)

# Global dictionary to store progress
download_status = {}

def progress_hook(d):
    """
    Callback hook for yt-dlp to update download progress.
    """
    if d['status'] == 'downloading':
        video_id = d.get('info_dict', {}).get('id', 'unknown')
        
        # Calculate percentage
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        
        if total_bytes:
            percent = (downloaded_bytes / total_bytes) * 100
        else:
            percent = 0
            
        download_status[video_id] = {
            'status': 'downloading',
            'percent': percent,
            'filename': d.get('filename', 'unknown'),
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0)
        }
    elif d['status'] == 'finished':
        video_id = d.get('info_dict', {}).get('id', 'unknown')
        download_status[video_id] = {
            'status': 'finished',
            'percent': 100,
            'filename': d.get('filename', 'unknown')
        }

@app.route('/api/analyze', methods=['POST'])
def analyze_playlist():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ydl_opts = {
        'extract_flat': True,  # Don't download, just extract info
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
                if entry: # entry can be None if video is deleted
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

def download_thread(url, folder_name, selected_ids):
    """
    Background thread to handle the download process.
    """
    # Create directory if it doesn't exist
    base_dir = os.path.join(os.getcwd(), 'downloads', folder_name)
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
        'progress_hooks': [progress_hook],
        'ignoreerrors': True,
    }

    # Filter for selected IDs if provided
    # Note: yt-dlp doesn't support filtering by ID easily in the main call for playlists without complex match_filter
    # So we will rely on the user passing the specific video URLs or we download the whole playlist.
    # For this implementation, to be robust, we will iterate and download selected items.
    
    # However, downloading one by one is slower. 
    # Optimization: Pass the full playlist URL but use 'match_filter' to select IDs.
    
    # Let's try a simpler approach: Download individual videos if selected_ids is provided.
    # Or if it's a full playlist download, use the playlist URL.
    
    # Actually, the robust way for a "playlist downloader" where you might pick songs:
    # Construct the list of URLs to download.
    
    urls_to_download = []
    if 'list=' in url and not selected_ids:
         urls_to_download = [url] # Download whole playlist
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

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url')
    folder_name = data.get('folder_name', 'Music')
    selected_ids = data.get('selected_ids', []) # List of video IDs

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Start download in a separate thread
    thread = threading.Thread(target=download_thread, args=(url, folder_name, selected_ids))
    thread.start()

    return jsonify({'status': 'started', 'message': 'Download started in background'})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(download_status)

@app.route('/api/library', methods=['GET'])
def get_library():
    """List all folders in the downloads directory."""
    base_dir = os.path.join(os.getcwd(), 'downloads')
    if not os.path.exists(base_dir):
        return jsonify([])
    
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    return jsonify(folders)

@app.route('/api/library/<folder>', methods=['GET'])
def get_folder_content(folder):
    """List all audio files in a specific folder."""
    folder_path = os.path.join(os.getcwd(), 'downloads', folder)
    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder not found'}), 404
        
    files = []
    # Extensions to look for
    extensions = ['*.mp3', '*.webm', '*.m4a', '*.wav']
    
    for ext in extensions:
        for filepath in glob.glob(os.path.join(folder_path, ext)):
            filename = os.path.basename(filepath)
            # Try to find a matching thumbnail (jpg, png, webp)
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

@app.route('/api/stream/<path:filepath>', methods=['GET'])
def stream_file(filepath):
    """Serve a file from the downloads directory."""
    # Security check: ensure we don't traverse up
    safe_path = os.path.normpath(os.path.join(os.getcwd(), 'downloads', filepath))
    if not safe_path.startswith(os.path.join(os.getcwd(), 'downloads')):
        return jsonify({'error': 'Access denied'}), 403
        
    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
        
    return send_file(safe_path)

@app.route('/')
def index():
    """Serve the main HTML file."""
    return send_file('index.html')

@app.route('/api/mobile/info', methods=['GET'])
def get_mobile_info():
    """Get network information for mobile access."""
    try:
        # Try to find the best local IP address
        local_ip = '127.0.0.1'
        
        # Method 1: Connect to a public DNS (most reliable if internet available)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            # Method 2: Iterate interfaces (fallback)
            try:
                # This is a simple heuristic fallback
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
            except:
                pass
        
        port = 5001
        mobile_url = f"http://{local_ip}:{port}/mobile"
        
        return jsonify({
            'ip': local_ip,
            'port': port,
            'url': mobile_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mobile')
def mobile_interface():
    """Serve the mobile HTML interface."""
    return send_file('mobile.html')

@app.route('/test-mobile')
def test_mobile():
    """Serve the mobile connectivity test page."""
    return send_file('test-mobile.html')

@app.route('/qr')
def qr_page():
    """Serve the QR code generator page."""
    return send_file('qr.html')

@app.route('/api/mobile/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """Force download a file from the downloads directory."""
    # Security check: ensure we don't traverse up
    safe_path = os.path.normpath(os.path.join(os.getcwd(), 'downloads', filepath))
    if not safe_path.startswith(os.path.join(os.getcwd(), 'downloads')):
        return jsonify({'error': 'Access denied'}), 403
        
    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Get just the filename for Content-Disposition
    filename = os.path.basename(safe_path)
    
    # Force download with attachment header
    return send_file(
        safe_path,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/library/random', methods=['GET'])
def get_random_songs():
    """Get a random selection of songs from all folders."""
    import random
    
    base_dir = os.path.join(os.getcwd(), 'downloads')
    if not os.path.exists(base_dir):
        return jsonify([])
    
    all_songs = []
    extensions = ['*.mp3', '*.webm', '*.m4a', '*.wav']
    
    # Walk through all folders
    for root, dirs, files in os.walk(base_dir):
        # Get relative path from base_dir
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            continue
        
        for filename in files:
            if any(filename.endswith(ext.replace('*', '')) for ext in extensions):
                base_name = os.path.splitext(filename)[0]
                
                # Try to find thumbnail
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
    
    # Shuffle and pick up to 20
    random.shuffle(all_songs)
    return jsonify(all_songs[:20])

# --- Statistics Logic ---
STATS_FILE = 'stats.json'

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_stats(stats):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")

@app.route('/api/stats/track', methods=['POST'])
def track_stat():
    data = request.json
    event_type = data.get('type') # 'play', 'time_update'
    song_id = data.get('song_id') # Use filename or title as ID
    duration = data.get('duration', 0) # For 'time_update'
    
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
        import time
        stats[song_id]['last_played'] = time.time()
    elif event_type == 'time_update':
        # Add duration in seconds
        stats[song_id]['total_time'] += duration
        
    save_stats(stats)
    return jsonify({'status': 'ok'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = load_stats()
    
    # Calculate derived stats
    if not stats:
        return jsonify({
            'most_played': None,
            'most_time': None,
            'least_played': None,
            'never_played': [],
            'total_plays': 0,
            'total_time_global': 0,
            'top_folders': [],
            'achievements': [],
            'first_played': None,
            'last_played': None,
            'library_explored_percent': 0,
            'unique_songs_played': 0
        })
        
    # Convert dict to list for sorting
    songs_list = []
    for sid, data in stats.items():
        data['id'] = sid
        songs_list.append(data)
        
    # Most played
    songs_list.sort(key=lambda x: x['play_count'], reverse=True)
    most_played = songs_list[0] if songs_list else None
    
    # Most time
    songs_list.sort(key=lambda x: x['total_time'], reverse=True)
    most_time = songs_list[0] if songs_list else None
    
    # Least played (of those that have been played)
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
    
    # Never played logic + folder stats
    base_dir = os.path.join(os.getcwd(), 'downloads')
    all_files = []
    folder_stats = {}
    extensions = ['*.mp3', '*.webm', '*.m4a', '*.wav']
    
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            rel_path = os.path.relpath(root, base_dir)
            if rel_path == '.':
                continue
                
            for filename in files:
                if any(filename.endswith(ext.replace('*', '')) for ext in extensions):
                    all_files.append(filename)
                    
                    # Track folder stats
                    if rel_path not in folder_stats:
                        folder_stats[rel_path] = {
                            'name': rel_path,
                            'play_count': 0,
                            'total_time': 0,
                            'song_count': 0
                        }
                    folder_stats[rel_path]['song_count'] += 1
                    
                    # Add stats if song has been played
                    if filename in stats:
                        folder_stats[rel_path]['play_count'] += stats[filename]['play_count']
                        folder_stats[rel_path]['total_time'] += stats[filename]['total_time']
    
    never_played = []
    for fname in all_files:
        if fname not in stats:
            never_played.append(fname)
    
    # Top folders
    top_folders = sorted(folder_stats.values(), key=lambda x: x['play_count'], reverse=True)[:3]
            
    # Global totals
    total_plays = sum(s['play_count'] for s in songs_list)
    total_time_global = sum(s['total_time'] for s in songs_list)
    unique_songs_played = len(songs_list)
    total_songs = len(all_files)
    library_explored_percent = (unique_songs_played / total_songs * 100) if total_songs > 0 else 0
    
    # Achievements
    achievements = []
    
    # Time-based achievements
    if total_time_global >= 360000:  # 100 hours
        achievements.append({'id': 'marathon', 'icon': '🏃', 'title': 'Maratonista', 'desc': '100+ horas'})
    elif total_time_global >= 36000:  # 10 hours
        achievements.append({'id': 'listener', 'icon': '🎧', 'title': 'Oyente Dedicado', 'desc': '10+ horas'})
    
    # Exploration achievements
    if library_explored_percent >= 75:
        achievements.append({'id': 'explorer', 'icon': '🗺️', 'title': 'Explorador', 'desc': '75% biblioteca'})
    elif library_explored_percent >= 50:
        achievements.append({'id': 'adventurer', 'icon': '🧭', 'title': 'Aventurero', 'desc': '50% biblioteca'})
    
    # Collection achievements
    if total_songs >= 100:
        achievements.append({'id': 'collector', 'icon': '💎', 'title': 'Coleccionista', 'desc': '100+ canciones'})
    elif total_songs >= 50:
        achievements.append({'id': 'enthusiast', 'icon': '⭐', 'title': 'Entusiasta', 'desc': '50+ canciones'})
    
    # Play count achievements
    if total_plays >= 500:
        achievements.append({'id': 'addict', 'icon': '🔥', 'title': 'Adicto Musical', 'desc': '500+ plays'})
    elif total_plays >= 100:
        achievements.append({'id': 'fan', 'icon': '🎵', 'title': 'Super Fan', 'desc': '100+ plays'})
    
    return jsonify({
        'most_played': most_played,
        'most_time': most_time,
        'least_played': least_played,
        'never_played': never_played[:50],
        'total_plays': total_plays,
        'total_time_global': total_time_global,
        'top_folders': top_folders,
        'achievements': achievements,
        'first_played': first_played,
        'last_played': last_played,
        'library_explored_percent': round(library_explored_percent, 1),
        'unique_songs_played': unique_songs_played,
        'total_songs': total_songs
    })



if __name__ == '__main__':
    # Ensure ffmpeg is available or warn user? 
    # yt-dlp usually needs ffmpeg for audio conversion.
    print("Starting server on http://0.0.0.0:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
