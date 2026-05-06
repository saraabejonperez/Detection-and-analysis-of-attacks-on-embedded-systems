from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Modelo(db.Model):
    __tablename__ = 'modelos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow())
    fecha_ultimo_uso = db.Column(db.DateTime, default=datetime.utcnow())

    usuario = db.relationship('User', backref=db.backref('modelos', lazy=True))