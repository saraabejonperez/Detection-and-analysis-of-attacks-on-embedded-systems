import os
from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Clave secreta necesaria para las sesiones y los mensajes flash
    app.secret_key = 'super_secret_key_tfg_change_in_production'
    
    # Configuración de la base de datos SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes.pages.main import main_bp
    from .routes.pages.dashboard import dashboard_bp
    from .routes.auth import auth_bp
    from .routes.pages.modelos import modelos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(modelos_bp)

    return app