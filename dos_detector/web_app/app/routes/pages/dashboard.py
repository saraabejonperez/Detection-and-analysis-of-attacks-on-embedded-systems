import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, session, flash
import pytz
from ...models import db, Modelo, Dispositivo

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def dashboard():
    is_guest = session.get('guest', False)
    username = session.get('username', 'Invitado')
    
    if not is_guest:
        user_id = session.get('user_id')
        
        if user_id:
            limite_fecha = datetime.now(pytz.timezone('Europe/Madrid')) - timedelta(days=40)
            
            modelos_caducados = Modelo.query.filter(
                Modelo.usuario_id == user_id, 
                Modelo.fecha_ultimo_uso < limite_fecha
            ).all()
            
            dispositivos_caducados = Dispositivo.query.filter(
                Dispositivo.usuario_id == user_id, 
                Dispositivo.fecha_ultimo_uso < limite_fecha
            ).all()
            
            hubo_limpieza = False

            for modelo in modelos_caducados:
                if modelo.ruta_archivo and os.path.exists(modelo.ruta_archivo):
                    os.remove(modelo.ruta_archivo)
                for config in modelo.archivos_config:
                    if config.ruta_archivo and os.path.exists(config.ruta_archivo):
                        os.remove(config.ruta_archivo)
                db.session.delete(modelo)
                hubo_limpieza = True

            for disp in dispositivos_caducados:
                db.session.delete(disp)
                hubo_limpieza = True

            if hubo_limpieza:
                db.session.commit()
                flash("Mantenimiento automático: Se han eliminado modelos y/o dispositivos inactivos por más de 40 días.", "warning")

    return render_template("dashboard.html", username=username, is_guest=is_guest)