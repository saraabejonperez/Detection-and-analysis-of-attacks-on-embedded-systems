from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

class User(db.Model):
    """
    Represent a user in the system.
    
    :ivar id: Unique identifier for the user.
    :type id: int
    :ivar username: Unique login name for the user.
    :type username: str
    :ivar password_hash: Securely hashed password.
    :type password_hash: str
    :ivar fecha_registro: Timestamp of when the user was created.
    :type fecha_registro: datetime.datetime
    :ivar is_admin: Flag indicating if the user has administrator privileges.
    :type is_admin: bool
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')))
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """
        Return a string representation of the User instance.

        :return: A string identifying the user by their username.
        :rtype: str
        """
        return f'<User {self.username}>'


class Modelo(db.Model):
    """
    Represent a model entity uploaded or created by a user.

    :ivar id: Unique identifier for the model.
    :type id: int
    :ivar nombre: Name of the model.
    :type nombre: str
    :ivar ruta_archivo: File system path where the model's main file is stored.
    :type ruta_archivo: str
    :ivar usuario_id: Foreign key referencing the user who owns the model.
    :type usuario_id: int
    :ivar fecha_subida: Timestamp of when the model was uploaded.
    :type fecha_subida: datetime.datetime
    :ivar fecha_ultimo_uso: Timestamp of when the model was last accessed or used.
    :type fecha_ultimo_uso: datetime.datetime
    :ivar usuario: Relationship referencing the owner `User` of this model.
    :type usuario: User
    """
    __tablename__ = 'modelos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')))
    fecha_ultimo_uso = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')))

    usuario = db.relationship('User', backref=db.backref('modelos', cascade="all, delete-orphan", lazy=True))

class File(db.Model):
    """
    Represent a configuration or complementary file associated with a specific model.

    :ivar id: Unique identifier for the file.
    :type id: int
    :ivar nombre: Name of the file.
    :type nombre: str
    :ivar ruta_archivo: File system path where the file is stored.
    :type ruta_archivo: str
    :ivar modelo_id: Foreign key referencing the parent model.
    :type modelo_id: int
    :ivar modelo: Relationship referencing the parent `Modelo` of this file.
    :type modelo: Modelo
    """
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelos.id'), nullable=False)
    
    modelo = db.relationship('Modelo', backref=db.backref('archivos_config', cascade="all, delete-orphan", lazy=True))

class Dispositivo(db.Model):
    """
    Represent a device associated with a user.

    :ivar id: Unique identifier for the device.
    :type id: int
    :ivar nombre: Name of the device.
    :type nombre: str
    :ivar ip: IP address assigned to the device.
    :type ip: str
    :ivar usuario_id: Foreign key referencing the user who registered the device.
    :type usuario_id: int
    :ivar fecha_registro: Timestamp of when the device was registered.
    :type fecha_registro: datetime.datetime
    :ivar fecha_ultimo_uso: Timestamp of when the device was last used.
    :type fecha_ultimo_uso: datetime.datetime
    :ivar usuario: Relationship referencing the owner `User` of this device.
    :type usuario: User
    """
    __tablename__ = 'dispositivos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')))
    fecha_ultimo_uso = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Madrid')))

    usuario = db.relationship('User', backref=db.backref('dispositivos', cascade="all, delete-orphan", lazy=True))