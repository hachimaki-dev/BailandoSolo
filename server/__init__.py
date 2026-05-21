"""
Bailando Solo — Flask application factory.
"""

from flask import Flask
from flask_cors import CORS


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # Register all route blueprints
    from server.routes.profiles import profiles_bp, ensure_default_profile
    from server.routes.downloads import downloads_bp
    from server.routes.library import library_bp
    from server.routes.stats import stats_bp
    from server.routes.mobile import mobile_bp

    app.register_blueprint(profiles_bp)
    app.register_blueprint(downloads_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(mobile_bp)

    # Initialize profiles on startup
    print("Initializing profiles system...")
    ensure_default_profile()
    print("Profiles initialized successfully!")

    return app
