"""
Bailando Solo — Tunnel Manager.
Creates secure HTTPS tunnels (via Cloudflare Tunnel or localtunnel)
to bypass restrictive local networks, AP isolation, and university firewalls.
"""

import re
import time
import shutil
import threading
import subprocess
import atexit

from server.config import PORT

_tunnel_lock = threading.Lock()
_tunnel_process = None
_tunnel_url = None
_tunnel_type = None
_tunnel_error = None


def get_tunnel_status():
    """Get the current state of the tunnel."""
    global _tunnel_process, _tunnel_url, _tunnel_type, _tunnel_error
    with _tunnel_lock:
        if _tunnel_process:
            if _tunnel_process.poll() is None:
                return {
                    'running': True,
                    'url': _tunnel_url,
                    'mobile_url': f"{_tunnel_url}/mobile" if _tunnel_url else None,
                    'type': _tunnel_type,
                    'error': None
                }
            else:
                # Process terminated unexpectedly
                ret_code = _tunnel_process.returncode
                _tunnel_process = None
                _tunnel_url = None
                return {
                    'running': False,
                    'url': None,
                    'mobile_url': None,
                    'type': None,
                    'error': _tunnel_error or f"Túnel finalizado con código {ret_code}"
                }
        return {
            'running': False,
            'url': None,
            'mobile_url': None,
            'type': None,
            'error': _tunnel_error
        }


def start_tunnel(port=None):
    """
    Start an encrypted HTTPS tunnel forwarding to local Flask port.
    Prefers cloudflared, with localtunnel as fallback.
    """
    global _tunnel_process, _tunnel_url, _tunnel_type, _tunnel_error
    if port is None:
        port = PORT

    with _tunnel_lock:
        # If already running, return existing info
        if _tunnel_process and _tunnel_process.poll() is None:
            return {
                'status': 'already_running',
                'url': _tunnel_url,
                'mobile_url': f"{_tunnel_url}/mobile" if _tunnel_url else None,
                'type': _tunnel_type
            }

        _tunnel_url = None
        _tunnel_type = None
        _tunnel_error = None

        # Check for cloudflared
        cloudflared_path = shutil.which('cloudflared') or '/opt/homebrew/bin/cloudflared'
        if cloudflared_path and shutil.which(cloudflared_path):
            try:
                cmd = [cloudflared_path, 'tunnel', '--url', f'http://127.0.0.1:{port}']
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                _tunnel_process = proc
                _tunnel_type = 'cloudflared'

                # Read output in a short loop to capture trycloudflare.com URL
                start_time = time.time()
                discovered_url = None

                while time.time() - start_time < 12:
                    line = proc.stderr.readline()
                    if not line:
                        time.sleep(0.1)
                        if proc.poll() is not None:
                            break
                        continue
                    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                    if match:
                        discovered_url = match.group(0)
                        break

                if discovered_url:
                    _tunnel_url = discovered_url
                    return {
                        'status': 'started',
                        'url': _tunnel_url,
                        'mobile_url': f"{_tunnel_url}/mobile",
                        'type': 'cloudflared'
                    }
                else:
                    _tunnel_error = "No se pudo obtener la URL de Cloudflare en el tiempo límite"
                    stop_tunnel()
            except Exception as e:
                _tunnel_error = f"Error iniciando cloudflared: {str(e)}"
                _tunnel_process = None

        # Fallback to localtunnel via npx
        npx_path = shutil.which('npx')
        if npx_path:
            try:
                cmd = [npx_path, '-y', 'localtunnel', '--port', str(port)]
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                _tunnel_process = proc
                _tunnel_type = 'localtunnel'

                start_time = time.time()
                discovered_url = None

                while time.time() - start_time < 15:
                    line = proc.stdout.readline()
                    if not line:
                        time.sleep(0.1)
                        if proc.poll() is not None:
                            break
                        continue
                    match = re.search(r'https://[a-zA-Z0-9-]+\.loca\.lt', line)
                    if match:
                        discovered_url = match.group(0)
                        break

                if discovered_url:
                    _tunnel_url = discovered_url
                    return {
                        'status': 'started',
                        'url': _tunnel_url,
                        'mobile_url': f"{_tunnel_url}/mobile",
                        'type': 'localtunnel'
                    }
                else:
                    _tunnel_error = "No se pudo obtener la URL de Localtunnel"
                    stop_tunnel()
            except Exception as e:
                _tunnel_error = f"Error iniciando localtunnel: {str(e)}"
                _tunnel_process = None

        err = _tunnel_error or "No se encontró cloudflared ni npx para crear el túnel"
        return {'status': 'error', 'error': err}


def stop_tunnel():
    """Terminate any active tunnel process."""
    global _tunnel_process, _tunnel_url, _tunnel_type
    with _tunnel_lock:
        if _tunnel_process:
            try:
                _tunnel_process.terminate()
                _tunnel_process.wait(timeout=3)
            except Exception:
                try:
                    _tunnel_process.kill()
                except Exception:
                    pass
            _tunnel_process = None
        _tunnel_url = None
        _tunnel_type = None
        return {'status': 'stopped'}


# Automatically cleanup tunnel process on app shutdown
atexit.register(stop_tunnel)
