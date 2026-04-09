from flask import Flask
from flask_cors import CORS

def create_app():

    app = Flask(__name__)
    CORS(app)

    # API routes
    from .routes.health import health_bp

    # Pages (frontend)
    from .routes.pages.dashboard import dashboard_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp)

    return app