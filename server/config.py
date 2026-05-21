"""
Bailando Solo — Configuration constants.
Single source of truth for paths, ports, and settings.
"""

import os

# Server
PORT = int(os.environ.get('BAILANDO_PORT', 5001))
HOST = '0.0.0.0'

# Paths (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, 'downloads')
PROFILES_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'profiles.json')
STATS_FILE = os.path.join(PROJECT_ROOT, 'stats.json')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
UI_DIST_DIR = os.path.join(PROJECT_ROOT, 'ui', 'dist')

# Audio file extensions (used by library and stats)
AUDIO_EXTENSIONS = ['.mp3', '.webm', '.m4a', '.wav']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
