"""
Bailando Solo — Mobile routes.
Handles mobile interface, QR page, file downloads, and folder ZIP downloads.
"""

import os
import socket
import shutil
import tempfile

from flask import Blueprint, jsonify, send_file, after_this_request

from server.config import PORT, DOWNLOADS_DIR, STATIC_DIR
from server.routes.profiles import load_profiles

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
        return jsonify({'ip': local_ip, 'port': PORT, 'url': mobile_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/api/ping', methods=['GET'])
def ping():
    """Fast health check endpoint for mobile offline/online detection."""
    return jsonify({'status': 'ok', 'server': 'BailandoSolo', 'version': '2.1'}), 200


@mobile_bp.route('/mobile')
def mobile_interface():
    """Serve the mobile HTML interface."""
    return send_file(os.path.join(STATIC_DIR, 'mobile.html'))


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

