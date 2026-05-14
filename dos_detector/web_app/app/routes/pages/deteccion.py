import os
import subprocess
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
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for('auth.login'))
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
            subprocess.run(["adb", "start-server"], check=False)
            #subprocess.run(["adb", "devices"], check=False)

            target = f"{device_ip}:5555"
            con_res = subprocess.run(["adb", "connect", target], capture_output=True, text=True)
            
            if "cannot connect" in con_res.stdout.lower() or "failed" in con_res.stdout.lower():
                flash(f"El dispositivo en {device_ip} no está accesible. Comprueba que está encendido y conectado a la red.", "error")
                return redirect(url_for("deteccion.index"))

            remote_dir = f"/home/{username}/modelos_ia"
            subprocess.run(["adb", "-s", target, "shell", f"mkdir -p {remote_dir}"], check=False)

            push_m = subprocess.run(["adb", "-s", target, "push", ruta_modelo, remote_dir], capture_output=True, text=True)
            push_f = subprocess.run(["adb", "-s", target, "push", ruta_features, remote_dir], capture_output=True, text=True)

            if push_m.returncode == 0 and push_f.returncode == 0:
                flash(f"Modelo transferido con éxito a {device_ip} en {remote_dir}.", "success")
            else:
                flash("Error durante la transferencia de archivos al dispositivo.", "error")
                print(f"Error ADB: {push_m.stderr} | {push_f.stderr}")

            subprocess.run(["adb", "disconnect", target], check=False)

        except FileNotFoundError:
            flash("Error Crítico: El comando ADB no está instalado en el servidor Docker.", "error")
        except Exception as e:
            flash(f"Ocurrió un error inesperado al contactar con el M5Stack: {str(e)}", "error")

        return redirect(url_for("deteccion.index"))

    return render_template("deteccion.html", modelos=modelos, dispositivos=dispositivos)