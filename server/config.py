"""
Bailando Solo — Configuration constants.
Single source of truth for paths, ports, and settings.
"""

import os
import sys

# Server
PORT = int(os.environ.get('BAILANDO_PORT', 5001))
HOST = '0.0.0.0'

# Paths
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if os.path.exists(os.path.join(BASE_DIR, 'static')):
        STATIC_DIR = os.path.join(BASE_DIR, 'static')
    elif os.path.exists(os.path.join(os.path.dirname(sys.executable), 'static')):
        STATIC_DIR = os.path.join(os.path.dirname(sys.executable), 'static')
    else:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

# User Data (stored in user home directory to prevent permission issues when packaged)
USER_DATA_DIR = os.path.expanduser('~/.bailandosolo')
os.makedirs(USER_DATA_DIR, exist_ok=True)

DOWNLOADS_DIR = os.path.join(USER_DATA_DIR, 'downloads')
PROFILES_CONFIG_FILE = os.path.join(USER_DATA_DIR, 'profiles.json')
STATS_FILE = os.path.join(USER_DATA_DIR, 'stats.json')
PLAYLISTS_FILE = os.path.join(USER_DATA_DIR, 'playlists.json')

# Audio file extensions (used by library and stats)
AUDIO_EXTENSIONS = ['.mp3', '.webm', '.m4a', '.wav']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

