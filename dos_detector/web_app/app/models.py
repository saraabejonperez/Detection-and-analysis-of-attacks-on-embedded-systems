from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Modelo(db.Model):
    __tablename__ = 'modelos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    fecha_subida = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))
    fecha_ultimo_uso = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))

    usuario = db.relationship('User', backref=db.backref('modelos', lazy=True))

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelos.id'), nullable=False)
    
    modelo = db.relationship('Modelo', backref=db.backref('archivos_config', cascade="all, delete-orphan", lazy=True))

class Dispositivo(db.Model):
    __tablename__ = 'dispositivos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))
    fecha_ultimo_uso = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Madrid')))

    usuario = db.relationship('User', backref=db.backref('dispositivos', cascade="all, delete-orphan", lazy=True))