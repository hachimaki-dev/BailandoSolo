"""
Bailando Solo — Entry point.
Run with: python3 server.py
"""

import sys
import os
import multiprocessing

# Required for PyInstaller frozen executables
multiprocessing.freeze_support()

from server import create_app
from server.config import HOST, PORT

app = create_app()

if __name__ == '__main__':
    is_frozen = getattr(sys, 'frozen', False)
    debug_mode = not is_frozen and os.environ.get('FLASK_DEBUG', '0') == '1'
    print(f"Starting server on http://{HOST}:{PORT} (frozen={is_frozen}, debug={debug_mode})")
    app.run(debug=debug_mode, use_reloader=debug_mode, host=HOST, port=PORT)
