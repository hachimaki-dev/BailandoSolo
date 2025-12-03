import os
import json
import threading
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

if __name__ == '__main__':
    # Ensure ffmpeg is available or warn user? 
    # yt-dlp usually needs ffmpeg for audio conversion.
    print("Starting server on http://localhost:5001")
    app.run(debug=True, port=5001)
