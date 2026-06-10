from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pytz
from ...models import db, Dispositivo


dispositivos_bp = Blueprint("dispositivos", __name__)


class DispositivoInvitado:
    """
    A lightweight data structure to represent a device for guest users.
    """
    def __init__(self, nombre, ip, fecha_registro):
        """
        Initialize a new guest device instance.

        :param nombre: Name assigned to the device.
        :type nombre: str
        :param ip: The IP address of the device.
        :type ip: str
        :param fecha_registro: A string representation of the registration timestamp.
        :type fecha_registro: str
        """
        self.nombre = nombre
        self.ip = ip
        self.fecha_registro = datetime.strptime(fecha_registro, '%Y-%m-%d %H:%M:%S')
        self.fecha_ultimo_uso = self.fecha_registro


@dispositivos_bp.route("/dispositivos", methods=["GET"])
def index():
    """
    Render the device management dashboard.

    :return: The rendered HTML template displaying the list of devices.
    :rtype: str | Response
    """
    if session.get('guest'):
        datos_invitado = session.get('guest_devices', [])
        dispositivos = [DispositivoInvitado(d['nombre'], d['ip'], d['fecha_registro']) for d in datos_invitado]
    
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        dispositivos = Dispositivo.query.filter_by(usuario_id=user_id).order_by(Dispositivo.fecha_registro.desc()).all()
    
    return render_template("dispositivos.html", dispositivos=dispositivos)


@dispositivos_bp.route("/dispositivos/add", methods=["POST"])
def add():
    """
    Register a new edge device.

    :return: A redirect response back to the device management dashboard.
    :rtype: Response
    """
    nombre = request.form.get('nombre_dispositivo')
    ip = request.form.get('ip_dispositivo')

    if not nombre or not ip:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("dispositivos.index"))

    if session.get('guest'):
        if 'guest_devices' not in session:
            session['guest_devices'] = []
            
        session['guest_devices'].append({
            'nombre': nombre,
            'ip': ip,
            'fecha_registro': datetime.now(pytz.timezone('Europe/Madrid')).strftime('%Y-%m-%d %H:%M:%S')
        })
        session.modified = True
        flash("Dispositivo registrado con éxito.", "success")
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
            
        nuevo_dispositivo = Dispositivo(nombre=nombre, ip=ip, usuario_id=user_id)
        db.session.add(nuevo_dispositivo)
        db.session.commit()
        flash("Dispositivo registrado con éxito.", "success")
        
    return redirect(url_for("dispositivos.index"))


@dispositivos_bp.route("/dispositivos/delete/<int:device_id>", methods=["POST"])
def delete(device_id):
    """
    Delete a specific device from the user's account or guest session.

    :param device_id: The unique identifier (database ID or list index) of the device.
    :type device_id: int
    :return: A redirect response back to the device management dashboard.
    :rtype: Response
    """
    if session.get('guest'):
        guest_devices = session.get('guest_devices', [])
        if 0 <= device_id < len(guest_devices):
            guest_devices.pop(device_id)
            session['guest_devices'] = guest_devices
            session.modified = True
            flash("Dispositivo eliminado.", "success")
        else:
            flash("Error al eliminar el dispositivo.", "error")
    else:
        user_id = session.get('user_id')
        dispositivo = Dispositivo.query.filter_by(id=device_id, usuario_id=user_id).first()
        
        if dispositivo:
            db.session.delete(dispositivo)
            db.session.commit()
            flash(f"Dispositivo '{dispositivo.nombre}' eliminado.", "success")
        else:
            flash("Error: No tienes permiso para eliminar este dispositivo.", "error")

    return redirect(url_for("dispositivos.index"))