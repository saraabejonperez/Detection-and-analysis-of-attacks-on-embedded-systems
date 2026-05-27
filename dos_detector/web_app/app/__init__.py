import os
from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    app.secret_key = os.urandom(24)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes.pages.main import main_bp
    from .routes.pages.dashboard import dashboard_bp
    from .routes.auth import auth_bp
    from .routes.pages.modelos import modelos_bp
    from .routes.pages.dispositivos import dispositivos_bp
    from .routes.pages.evaluacion import evaluacion_bp
    from .routes.pages.cuenta import cuenta_bp
    from .routes.pages.deteccion import deteccion_bp
    from .routes.pages.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(modelos_bp)
    app.register_blueprint(dispositivos_bp)
    app.register_blueprint(evaluacion_bp)
    app.register_blueprint(cuenta_bp)
    app.register_blueprint(deteccion_bp)
    app.register_blueprint(admin_bp)

    return app