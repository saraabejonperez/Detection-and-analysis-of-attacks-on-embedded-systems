import os
import paramiko
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from ...models import db, Modelo, Dispositivo, User

deteccion_bp = Blueprint("deteccion", __name__)

@deteccion_bp.route("/deteccion", methods=["GET", "POST"])
def index():
    if session.get('guest'):
        modelos = session.get('guest_models', [])
        dispositivos = session.get('guest_devices', [])
        username = "guest"
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
            
        user = User.query.get(user_id)
        username = user.username
        modelos = Modelo.query.filter_by(usuario_id=user_id).all()
        dispositivos = Dispositivo.query.filter_by(usuario_id=user_id).all()

    if request.method == "POST":
        model_id = request.form.get("model_id")
        device_id = request.form.get("device_id")

        if model_id is None or device_id is None or model_id == "" or device_id == "":
            flash("Debes seleccionar un modelo y un dispositivo.", "error")
            return redirect(url_for("deteccion.index"))

        ruta_modelo, ruta_features, device_ip = None, None, None
        
        try:
            if session.get('guest'):
                idx_m, idx_d = int(model_id), int(device_id)
                ruta_modelo = modelos[idx_m]['ruta_archivo']
                ruta_features = modelos[idx_m]['ruta_features']
                device_ip = dispositivos[idx_d]['ip']
            else:
                modelo_db = Modelo.query.filter_by(id=model_id, usuario_id=user_id).first()
                disp_db = Dispositivo.query.filter_by(id=device_id, usuario_id=user_id).first()
                if modelo_db and disp_db:
                    ruta_modelo = modelo_db.ruta_archivo
                    ruta_features = modelo_db.archivos_config[0].ruta_archivo if modelo_db.archivos_config else None
                    device_ip = disp_db.ip
        except Exception:
            flash("Error al recuperar los datos seleccionados.", "error")
            return redirect(url_for("deteccion.index"))

        if not ruta_modelo or not os.path.exists(ruta_modelo) or not ruta_features or not os.path.exists(ruta_features):
            flash("Los archivos del modelo no se encuentran en el servidor.", "error")
            return redirect(url_for("deteccion.index"))
        if not device_ip:
            flash("El dispositivo no tiene una IP válida.", "error")
            return redirect(url_for("deteccion.index"))

        try:
            DEVICE_USER = "root"
            DEVICE_PASS = "1234root"
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(device_ip, port=22, username=DEVICE_USER, password=DEVICE_PASS, timeout=10)

            remote_dir = f"/home/DoSDetectionSystem{username}"
            ssh.exec_command(f"mkdir -p {remote_dir}")

            sftp = ssh.open_sftp()
            
            dest_modelo = f"{remote_dir}/{os.path.basename(ruta_modelo)}"
            sftp.put(ruta_modelo, dest_modelo)
            
            dest_features = f"{remote_dir}/{os.path.basename(ruta_features)}"
            sftp.put(ruta_features, dest_features)
            
            sftp.close()
            ssh.close()

            flash(f"Archivos transferidos con éxito a {device_ip} mediante SSH.", "success")

        except paramiko.AuthenticationException:
            flash("Error: Credenciales SSH incorrectas (Usuario/Contraseña del dispositivo).", "error")
        except paramiko.ssh_exception.NoValidConnectionsError:
            flash(f"No se pudo acceder a la IP {device_ip}. ¿Está conectado a la misma red Wi-Fi?", "error")
        except Exception as e:
            flash(f"Error inesperado en la conexión: {str(e)}", "error")

        return redirect(url_for("deteccion.index"))

    return render_template("deteccion.html", modelos=modelos, dispositivos=dispositivos)