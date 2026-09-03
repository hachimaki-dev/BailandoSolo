"""
Bailando Solo — Mobile routes.
Handles mobile interface, QR page, file downloads, and folder ZIP downloads.
"""

import os
import socket
import shutil
import tempfile

import time
import threading
from flask import Blueprint, jsonify, send_file, after_this_request, request

from server.config import PORT, DOWNLOADS_DIR, STATIC_DIR
from server.routes.profiles import load_profiles
from server.tunnel import start_tunnel, stop_tunnel, get_tunnel_status
from server.state import get_download_status, update_download_status
import yt_dlp
from server.routes.downloads import _build_ydl_options

mobile_bp = Blueprint('mobile', __name__)


@mobile_bp.route('/api/mobile/info', methods=['GET'])
def get_mobile_info():
    """Get network information for mobile access."""
    try:
        local_ip = '127.0.0.1'
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except OSError:
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
            except socket.gaierror:
                pass

        mobile_url = f"http://{local_ip}:{PORT}/mobile"
        tunnel_info = get_tunnel_status()
        return jsonify({
            'ip': local_ip,
            'port': PORT,
            'url': mobile_url,
            'tunnel': tunnel_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/api/ping', methods=['GET'])
def ping():
    """Fast health check endpoint for mobile offline/online detection."""
    return jsonify({'status': 'ok', 'server': 'BailandoSolo', 'version': '2.1'}), 200


@mobile_bp.route('/mobile')
def mobile_interface():
    """Serve the mobile HTML interface with cache-friendly headers for PWA."""
    response = send_file(os.path.join(STATIC_DIR, 'mobile.html'))
    # Allow SW to cache this response, but always revalidate with server when online
    response.headers['Cache-Control'] = 'public, max-age=0, must-revalidate'
    return response


@mobile_bp.route('/manifest.json')
@mobile_bp.route('/manifest.webmanifest')
def manifest_file():
    """Serve the PWA Web App Manifest."""
    return send_file(
        os.path.join(STATIC_DIR, 'manifest.json'),
        mimetype='application/manifest+json'
    )


@mobile_bp.route('/sw.js')
def service_worker():
    """Serve the Service Worker with correct headers for PWA registration."""
    response = send_file(
        os.path.join(STATIC_DIR, 'sw.js'),
        mimetype='application/javascript'
    )
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@mobile_bp.route('/test-mobile')
def test_mobile():
    """Serve the mobile connectivity test page."""
    return send_file(os.path.join(STATIC_DIR, 'test-mobile.html'))


@mobile_bp.route('/qr')
def qr_page():
    """Serve the QR code generator page."""
    return send_file(os.path.join(STATIC_DIR, 'qr.html'))


@mobile_bp.route('/api/mobile/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """Force download a file from the active profile's directory."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')

    safe_path = os.path.normpath(os.path.join(DOWNLOADS_DIR, active_profile, filepath))
    if not safe_path.startswith(os.path.join(DOWNLOADS_DIR, active_profile)):
        return jsonify({'error': 'Access denied'}), 403

    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404

    filename = os.path.basename(safe_path)
    return send_file(safe_path, as_attachment=True, download_name=filename)


@mobile_bp.route('/api/mobile/download-folder/<path:folder>', methods=['GET'])
def download_folder(folder):
    """Download an entire folder as a ZIP file."""
    config = load_profiles()
    active_profile = config.get('active', 'Default')

    folder_path = os.path.join(DOWNLOADS_DIR, active_profile, folder)
    safe_path = os.path.normpath(folder_path)
    base_downloads = os.path.join(DOWNLOADS_DIR, active_profile)

    if not safe_path.startswith(base_downloads):
        return jsonify({'error': 'Access denied'}), 403

    if not os.path.exists(safe_path):
        return jsonify({'error': 'Folder not found'}), 404

    try:
        temp_dir = tempfile.mkdtemp()
        folder_clean_name = os.path.basename(safe_path) or 'Album'
        zip_base_path = os.path.join(temp_dir, 'archive')

        # Create zip containing all files inside folder_path
        shutil.make_archive(zip_base_path, 'zip', root_dir=safe_path)
        zip_path = zip_base_path + '.zip'

        if not os.path.exists(zip_path):
            return jsonify({'error': 'Failed to create ZIP'}), 500

        @after_this_request
        def remove_temp(response):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Error removing temp dir: {e}")
            return response

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{folder_clean_name}.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/api/tunnel/status', methods=['GET'])
def tunnel_status():
    """Get current status and URL of the remote/university tunnel."""
    return jsonify(get_tunnel_status())


@mobile_bp.route('/api/tunnel/start', methods=['POST'])
def tunnel_start():
    """Start the HTTPS tunnel to allow remote and AP-isolated mobile devices to connect."""
    result = start_tunnel()
    if result.get('status') == 'error':
        return jsonify(result), 500
    return jsonify(result), 200


@mobile_bp.route('/api/tunnel/stop', methods=['POST'])
def tunnel_stop():
    """Stop the running HTTPS tunnel."""
    result = stop_tunnel()
    return jsonify(result), 200


def _mobile_download_thread(raw_query, folder_name, task_id):
    """
    Dedicated background download thread for mobile requests.
    Supports search queries and direct YouTube URLs.
    Accurately reports real-time progress to task_id in server.state.
    """
    try:
        config = load_profiles()
        active_profile = config.get('active', 'Default')
        base_dir = os.path.join(DOWNLOADS_DIR, active_profile, folder_name)
        os.makedirs(base_dir, exist_ok=True)

        is_url = raw_query.startswith('http://') or raw_query.startswith('https://')
        resolved_url = raw_query
        title_for_stage = raw_query

        # If it's a search term, resolve it to an actual YouTube video first
        if not is_url:
            update_download_status(task_id, {
                'status': 'searching',
                'stage': f'Buscando "{raw_query}" en YouTube...',
                'percent': 10.0,
                'speed': 0,
                'eta': 0
            })

            search_opts = _build_ydl_options({'extract_flat': True, 'quiet': True})
            with yt_dlp.YoutubeDL(search_opts) as s_ydl:
                search_res = s_ydl.extract_info(f"ytsearch1:{raw_query}", download=False)
                entries = search_res.get('entries', []) if search_res else []
                if not entries or not entries[0]:
                    update_download_status(task_id, {
                        'status': 'error',
                        'stage': 'No se encontraron resultados en YouTube',
                        'percent': 0,
                        'error': 'No results found'
                    })
                    return

                first_entry = entries[0]
                resolved_id = first_entry.get('id')
                resolved_url = f"https://www.youtube.com/watch?v={resolved_id}"
                title_for_stage = first_entry.get('title') or raw_query

        # Progress hook for yt-dlp
        def hook(d):
            status = d.get('status')
            if status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                raw_pct = (downloaded / total) * 100.0 if total > 0 else 0.0
                scaled_pct = min(92.0, max(15.0, round(raw_pct * 0.9, 1)))
                update_download_status(task_id, {
                    'status': 'downloading',
                    'stage': f'Descargando audio ({int(scaled_pct)}%)...',
                    'percent': scaled_pct,
                    'downloaded_bytes': downloaded,
                    'total_bytes': total,
                    'speed': d.get('speed') or 0,
                    'eta': d.get('eta') or 0,
                    'filename': os.path.basename(d.get('filename') or 'audio.mp3')
                })
            elif status == 'finished':
                update_download_status(task_id, {
                    'status': 'processing',
                    'stage': 'Extrayendo audio a MP3 y carátula...',
                    'percent': 95.0,
                    'speed': 0,
                    'eta': 0
                })

        update_download_status(task_id, {
            'status': 'downloading',
            'stage': f'Iniciando descarga: {title_for_stage[:35]}...',
            'percent': 15.0,
            'speed': 0,
            'eta': 0
        })

        base_ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }
            ],
            'outtmpl': os.path.join(base_dir, '%(title)s.%(ext)s'),
            'writethumbnail': True,
            'ignoreerrors': False,
            'progress_hooks': [hook],
            'quiet': True,
            'no_warnings': True,
        }

        ydl_opts = _build_ydl_options(base_ydl_opts)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(resolved_url, download=True)
            downloaded_title = info.get('title') if info else title_for_stage

        update_download_status(task_id, {
            'status': 'finished',
            'stage': 'Completado con éxito en tu PC',
            'percent': 100.0,
            'speed': 0,
            'eta': 0,
            'title': downloaded_title
        })

    except Exception as e:
        err_msg = str(e)
        print(f"[Mobile Download Error] {task_id}: {err_msg}")
        update_download_status(task_id, {
            'status': 'error',
            'stage': f'Error: {err_msg[:60]}',
            'percent': 0,
            'error': err_msg
        })


@mobile_bp.route('/api/mobile/quick-download', methods=['POST'])
def quick_download():
    """Trigger a fast download from mobile via YouTube URL or search query to active profile."""
    data = request.json or {}
    raw_query = (data.get('query') or data.get('url') or '').strip()
    folder_name = data.get('folder', 'Descargas').strip() or 'Descargas'

    if not raw_query:
        return jsonify({'error': 'Enlace de YouTube o nombre de canción requerido'}), 400

    task_id = f"mobile_{int(time.time() * 1000)}"

    update_download_status(task_id, {
        'status': 'waiting',
        'stage': 'Iniciando descarga en la PC...',
        'percent': 5.0,
        'speed': 0,
        'eta': 0
    })

    # Start download in background thread using dedicated mobile engine
    thread = threading.Thread(
        target=_mobile_download_thread,
        args=(raw_query, folder_name, task_id)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'status': 'started',
        'task_id': task_id,
        'folder': folder_name,
        'query': raw_query
    }), 200


@mobile_bp.route('/api/mobile/quick-status/<task_id>', methods=['GET'])
def quick_status(task_id):
    """Check progress of a specific mobile-initiated download."""
    all_status = get_download_status()
    task = all_status.get(task_id)
    if not task:
        return jsonify({'status': 'unknown', 'percent': 0}), 404
    return jsonify(task), 200



