import os, paramiko, time, pandas as pd
from datetime import datetime
import pytz
from flask import Blueprint, current_app, render_template, request, flash, session, redirect, url_for, jsonify
from ...models import db, Modelo, Dispositivo, User

deteccion_bp = Blueprint("deteccion", __name__)

ALARMAS_ACTIVAS = {}

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

    return render_template("deteccion.html", modelos=modelos, dispositivos=dispositivos)
    
@deteccion_bp.route("/api/transfer", methods=["POST"])
def api_transfer():
    model_id = request.form.get("model_id")
    device_id = request.form.get("device_id")
    device_user = request.form.get("device_user", "root")
    device_pass = request.form.get("device_pass", "")

    if not model_id or not device_id:
        return jsonify({"status": "error", "message": "Debes seleccionar un modelo y un dispositivo."}), 400

    username = session.get('username', 'guest')
    user_id = session.get('user_id')
    ruta_modelo, ruta_features, device_ip = None, None, None

    try:
        if session.get('guest'):
            idx_m, idx_d = int(model_id), int(device_id)
            modelos = session.get('guest_models', [])
            dispositivos = session.get('guest_devices', [])
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

                modelo_db.fecha_ultimo_uso = datetime.now(pytz.timezone('Europe/Madrid'))
                disp_db.fecha_ultimo_uso = datetime.now(pytz.timezone('Europe/Madrid'))
                db.session.commit()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error en base de datos: {str(e)}"}), 500

    if not ruta_modelo or not os.path.exists(ruta_modelo):
        return jsonify({"status": "error", "message": "El modelo no se encuentra en el servidor."}), 404
    if not device_ip:
        return jsonify({"status": "error", "message": "El dispositivo no tiene una IP válida."}), 400

    # Lógica SSH
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, port=22, username=device_user, password=device_pass, timeout=10)

        remote_dir = f"/home/DoSDetectionSystem/{username}"
        ssh.exec_command(f"mkdir -p {remote_dir}")

        sftp = ssh.open_sftp()
        sftp.put(ruta_modelo, f"{remote_dir}/{os.path.basename(ruta_modelo)}")
        if ruta_features:
            sftp.put(ruta_features, f"{remote_dir}/{os.path.basename(ruta_features)}")

        ruta_script = os.path.join(current_app.root_path, 'scripts', 'detection_edge.py')
        if os.path.exists(ruta_script):
            sftp.put(ruta_script, f"{remote_dir}/detection_edge.py")

        sftp.close()
        ssh.close()

        return jsonify({"status": "success", "message": "Archivos transferidos con éxito."}), 200

    except paramiko.AuthenticationException:
        return jsonify({"status": "error", "message": "Credenciales SSH incorrectas."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"No se pudo acceder a {device_ip} (Revisa conexión y red)"}), 500

@deteccion_bp.route("/api/alarm", methods=["POST"])
def receive_alarm():
    data = request.json
    device_ip = data.get("device_ip", request.remote_addr)
    
    if device_ip not in ALARMAS_ACTIVAS:
        ALARMAS_ACTIVAS[device_ip] = []
        
    ALARMAS_ACTIVAS[device_ip].append(data)
    return jsonify({"status": "ok"}), 200

@deteccion_bp.route("/api/poll_alarms/<device_ip>", methods=["GET"])
def poll_alarms(device_ip):
    alarmas = ALARMAS_ACTIVAS.pop(device_ip, [])
    return jsonify({"alarms": alarmas})

@deteccion_bp.route("/deteccion/start", methods=["POST"])
def start_detection():
    data = request.json
    device_ip = data.get("device_ip")
    model_id = data.get("model_id")
    device_user = data.get("device_user", "root")
    device_pass = data.get("device_pass", "")
    
    username = session.get('username', 'guest')
    user_id = session.get('user_id')
    remote_dir = f"/home/DoSDetectionSystem/{username}"
    
    nombre_modelo = "modelo.pkl"
    nombre_features = "features.npy"

    try:
        if session.get('guest'):
            modelos = session.get('guest_models', [])
            idx = int(model_id)
            ruta_modelo_local = modelos[idx]['ruta_archivo']
            ruta_features_local = modelos[idx]['ruta_features']
        else:
            modelo_db = Modelo.query.filter_by(id=model_id, usuario_id=user_id).first()
            if modelo_db:
                ruta_modelo_local = modelo_db.ruta_archivo
                ruta_features_local = modelo_db.archivos_config[0].ruta_archivo if modelo_db.archivos_config else ""
        
        if ruta_modelo_local:
            nombre_modelo = os.path.basename(ruta_modelo_local)
        if ruta_features_local:
            nombre_features = os.path.basename(ruta_features_local)
            
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al buscar nombres de archivos: {str(e)}"}), 500

    script_path = f"{remote_dir}/detection_edge.py"
    model_path = f"{remote_dir}/{nombre_modelo}"
    features_path = f"{remote_dir}/{nombre_features}"
    log_path = f"{remote_dir}/detection_log.txt"
    results_path = f"{remote_dir}/resultados.csv"
    
    webhook_url = f"http://{request.host}/api/alarm"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, port=22, username=device_user, password=device_pass, timeout=10)
        
        comando = (
            f"nohup python3 {script_path} "
            f"--model {model_path} "
            f"--features {features_path} "
            f"--ip {device_ip} "
            f"--webhook {webhook_url} "
            f"--log {log_path} "
            f"--results {results_path} "
            f"> /dev/null 2>&1 &"
        )
        
        ssh.exec_command(comando)
        ssh.close()
        
        return jsonify({"status": "success", "message": "Detección iniciada"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@deteccion_bp.route("/deteccion/stop", methods=["POST"])
def stop_detection():
    data = request.json
    device_ip = data.get("device_ip")
    device_user = data.get("device_user", "root")
    device_pass = data.get("device_pass", "")
    
    username = session.get('username', 'guest')
    remote_dir = f"/home/DoSDetectionSystem/{username}"
    results_remote_path = f"{remote_dir}/resultados.csv"
    
    local_results_path = os.path.join(current_app.root_path, '..', 'data', f"temp_results_{device_ip}.csv")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device_ip, port=22, username=device_user, password=device_pass, timeout=10)
        
        ssh.exec_command("pkill -f detection_edge.py")
        
        sftp = ssh.open_sftp()
        try:
            sftp.get(results_remote_path, local_results_path)
        except IOError:
            current_app.logger.error(f"Error descargando CSV: {e}")
            sftp.close()
            ssh.close()
            return jsonify({
                "flujos_totales": 0, "ataques": 0, "benignos": 0, "latencia_media": 0, "duracion_segundos": 0
            }), 200

        sftp.close()
        ssh.close()

        df = pd.read_csv(local_results_path)
        
        if df.empty:
            return jsonify({
                "flujos_totales": 0, "ataques": 0, "benignos": 0, "latencia_media": 0, "duracion_segundos": 0
            }), 200

        flujos_totales = len(df)
        ataques = len(df[df['label'] == 'DoS ATTACK'])
        benignos = flujos_totales - ataques
        latencia_media = round(df['latency'].mean(), 4)
        
        if os.path.exists(local_results_path):
            os.remove(local_results_path)

        return jsonify({
            "status": "success",
            "flujos_totales": flujos_totales,
            "ataques": ataques,
            "benignos": benignos,
            "latencia_media": latencia_media
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500