import os
import uuid
from datetime import datetime
import pytz
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from ...models import db, Modelo, File

modelos_bp = Blueprint("modelos", __name__)

class ModeloInvitado:
    def __init__(self, nombre, fecha_subida):
        self.nombre = nombre
        self.fecha_subida = datetime.strptime(fecha_subida, '%Y-%m-%d %H:%M:%S')
        self.fecha_ultimo_uso = self.fecha_subida

@modelos_bp.route("/modelos", methods=["GET"])
def index():
    if session.get('guest'):
        datos_invitado = session.get('guest_models', [])
        modelos = [ModeloInvitado(m['nombre'], m['fecha_subida']) for m in datos_invitado]
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        modelos = Modelo.query.filter_by(usuario_id=user_id).order_by(Modelo.fecha_subida.desc()).all()
    
    return render_template("modelos.html", modelos=modelos)

@modelos_bp.route("/modelos/upload", methods=["POST"])
def upload():
    if 'archivo_modelo' not in request.files or 'archivo_features' not in request.files:
        flash("Faltan archivos requeridos.", "error")
        return redirect(url_for("modelos.index"))
        
    file_model = request.files['archivo_modelo']
    file_features = request.files['archivo_features']
    
    if file_model.filename == '' or file_features.filename == '':
        flash("Debes seleccionar ambos archivos.", "error")
        return redirect(url_for("modelos.index"))
    
    timestamp = int(datetime.now(pytz.timezone('Europe/Madrid')).timestamp())
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'modelos')
    os.makedirs(upload_folder, exist_ok=True)
    
    name_model = secure_filename(file_model.filename)
    name_features = secure_filename(file_features.filename)

    if session.get('guest'):
        uid = session.get('guest_id', 'guest_temp')
        path_m = os.path.join(upload_folder, f"guest_{uid}_{timestamp}_{name_model}")
        path_f = os.path.join(upload_folder, f"guest_{uid}_{timestamp}_{name_features}")
    else:
        uid = session.get('user_id')
        path_m = os.path.join(upload_folder, f"user{uid}_{timestamp}_{name_model}")
        path_f = os.path.join(upload_folder, f"user{uid}_{timestamp}_{name_features}")

    file_model.save(path_m)
    file_features.save(path_f)

    if session.get('guest'):
        if 'guest_models' not in session: session['guest_models'] = []
        session['guest_models'].append({
            'nombre': name_model,
            'ruta_archivo': path_m,
            'ruta_features': path_f,
            'fecha_subida': datetime.now(pytz.timezone('Europe/Madrid')).strftime('%Y-%m-%d %H:%M:%S')
        })
        session.modified = True
    else:
        nuevo_modelo = Modelo(nombre=name_model, ruta_archivo=path_m, usuario_id=uid)
        db.session.add(nuevo_modelo)
        db.session.flush()
        
        nuevo_file = File(nombre=name_features, ruta_archivo=path_f, modelo_id=nuevo_modelo.id)
        db.session.add(nuevo_file)
        db.session.commit()
        
    flash("Modelo y configuración subidos correctamente.", "success")
    return redirect(url_for("modelos.index"))

@modelos_bp.route("/modelos/delete/<int:model_id>", methods=["POST"])
def delete(model_id):
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'modelos')
    
    if session.get('guest'):
        guest_models = session.get('guest_models', [])
        if 0 <= model_id < len(guest_models):
            modelo_data = guest_models.pop(model_id)
            
            file_path = modelo_data.get('ruta_archivo')
            features_path = modelo_data.get('ruta_features')
            
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            if features_path and os.path.exists(features_path):
                os.remove(features_path)
            
            session['guest_models'] = guest_models
            session.modified = True
            flash("Modelo y configuración eliminados.", "success")
        else:
            flash("No se pudo encontrar el modelo a eliminar.", "error")

    else:
        user_id = session.get('user_id')
        modelo = Modelo.query.filter_by(id=model_id, usuario_id=user_id).first()
        
        if modelo:
            file_path = modelo.ruta_archivo
            
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error al borrar archivo principal: {e}")
            
            for archivo_config in modelo.archivos_config:
                config_path = archivo_config.ruta_archivo
                if config_path and os.path.exists(config_path):
                    try:
                        os.remove(config_path)
                    except Exception as e:
                        print(f"Error al borrar archivo de configuración: {e}")
            
            db.session.delete(modelo)
            db.session.commit()
            flash(f"Modelo '{modelo.nombre}' eliminado correctamente.", "success")
        else:
            flash("Error: No tienes permiso para eliminar este modelo.", "error")

    return redirect(url_for("modelos.index"))