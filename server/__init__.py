"""
Bailando Solo — Flask application factory.
"""

from flask import Flask
from flask_cors import CORS

from server.config import STATIC_DIR


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Range'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Range, Accept-Ranges, Content-Length'
        response.headers['Accept-Ranges'] = 'bytes'
        return response

    # Register all route blueprints
    from server.routes.profiles import profiles_bp, ensure_default_profile
    from server.routes.downloads import downloads_bp
    from server.routes.library import library_bp
    from server.routes.stats import stats_bp
    from server.routes.mobile import mobile_bp
    from server.routes.playlists import playlists_bp

    app.register_blueprint(profiles_bp)
    app.register_blueprint(downloads_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(mobile_bp)
    app.register_blueprint(playlists_bp)

    # Initialize profiles on startup
    print("Initializing profiles system...")
    ensure_default_profile()
    print("Profiles initialized successfully!")

    return app
