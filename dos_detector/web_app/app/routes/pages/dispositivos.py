from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pytz
from ...models import db, Dispositivo

dispositivos_bp = Blueprint("dispositivos", __name__)

class DispositivoInvitado:
    def __init__(self, nombre, ip, fecha_registro):
        self.nombre = nombre
        self.ip = ip
        self.fecha_registro = datetime.strptime(fecha_registro, '%Y-%m-%d %H:%M:%S')
        self.fecha_ultimo_uso = self.fecha_registro

@dispositivos_bp.route("/dispositivos", methods=["GET"])
def index():
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