"""
Bailando Solo — Entry point.
Run with: python3 server.py
"""

from server import create_app
from server.config import HOST, PORT

app = create_app()

if __name__ == '__main__':
    print(f"Starting server on http://{HOST}:{PORT}")
    app.run(debug=True, host=HOST, port=PORT)
