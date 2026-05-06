import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from ...models import db, Modelo

modelos_bp = Blueprint("modelos", __name__)

# Clase falsa para imitar el comportamiento de la BD para los invitados
class ModeloInvitado:
    def __init__(self, nombre, fecha_subida):
        self.nombre = nombre
        self.fecha_subida = datetime.strptime(fecha_subida, '%Y-%m-%d %H:%M:%S')
        self.fecha_ultimo_uso = self.fecha_subida

@modelos_bp.route("/modelos", methods=["GET"])
def index():
    if session.get('guest'):
        # Leemos los modelos de la sesión y los convertimos en objetos para el HTML
        datos_invitado = session.get('guest_models', [])
        modelos = [ModeloInvitado(m['nombre'], m['fecha_subida']) for m in datos_invitado]
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        # Modelos reales de la base de datos
        modelos = Modelo.query.filter_by(usuario_id=user_id).order_by(Modelo.fecha_subida.desc()).all()
    
    return render_template("modelos.html", modelos=modelos)

@modelos_bp.route("/modelos/upload", methods=["POST"])
def upload():
    if 'archivo_modelo' not in request.files:
        flash("No se envió ningún archivo.", "error")
        return redirect(url_for("modelos.index"))
        
    file = request.files['archivo_modelo']
    
    if file.filename == '':
        flash("Ningún archivo seleccionado.", "error")
        return redirect(url_for("modelos.index"))
        
    if file:
        filename = secure_filename(file.filename)
        timestamp = int(datetime.utcnow().timestamp())
        
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'modelos')
        os.makedirs(upload_folder, exist_ok=True)
        
        # LOGICA PARA INVITADOS
        if session.get('guest'):
            # Generamos un ID de invitado si no tiene uno
            if 'guest_id' not in session:
                session['guest_id'] = str(uuid.uuid4())
                
            unique_filename = f"guest_{session['guest_id']}_{timestamp}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Guardamos la info en la sesión (no en la BD)
            if 'guest_models' not in session:
                session['guest_models'] = []
                
            session['guest_models'].append({
                'nombre': filename,
                'ruta_archivo': file_path,
                'fecha_subida': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })
            session.modified = True # Forzamos a Flask a guardar la cookie
            
        # LOGICA PARA USUARIOS REGISTRADOS
        else:
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('auth.login'))
                
            unique_filename = f"user{user_id}_{timestamp}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            nuevo_modelo = Modelo(
                nombre=filename,
                ruta_archivo=file_path,
                usuario_id=user_id
            )
            db.session.add(nuevo_modelo)
            db.session.commit()
            
        flash("Modelo subido con éxito.", "success")
        
    return redirect(url_for("modelos.index"))