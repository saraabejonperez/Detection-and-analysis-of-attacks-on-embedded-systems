import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from ...models import db, User, Modelo, Dispositivo

cuenta_bp = Blueprint("cuenta", __name__)

@cuenta_bp.route("/cuenta", methods=["GET", "POST"])
def index():
    if session.get('guest'):
        flash("La página de cuenta solo está disponible para usuarios registrados.", "neutral")
        return redirect(url_for('dashboard.dashboard'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return redirect(url_for('auth.login'))

    num_modelos = Modelo.query.filter_by(usuario_id=user_id).count()
    num_dispositivos = Dispositivo.query.filter_by(usuario_id=user_id).count()

    if request.method == "POST":
        nuevo_username = request.form.get("username").strip()
        nueva_pass = request.form.get("password").strip()

        if nuevo_username and nuevo_username != user.username:
            existente = User.query.filter_by(username=nuevo_username).first()
            if existente:
                flash("El nombre de usuario ya está en uso.", "error")
            else:
                user.username = nuevo_username
                session['username'] = nuevo_username
                db.session.commit()
                flash("Nombre de usuario actualizado.", "success")

        if nueva_pass:
            if len(nueva_pass) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "error")
            else:
                user.password_hash = generate_password_hash(nueva_pass)
                db.session.commit()
                flash("Contraseña actualizada correctamente.", "success")

        return redirect(url_for("cuenta.index"))

    return render_template("cuenta.html", 
                           user=user, 
                           num_modelos=num_modelos, 
                           num_dispositivos=num_dispositivos)

@cuenta_bp.route("/cuenta/delete", methods=["POST"])
def delete_account():
    if session.get('guest'):
        return redirect(url_for('main.index'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if user:
        try:
            modelos_usuario = Modelo.query.filter_by(usuario_id=user_id).all()
            for modelo in modelos_usuario:
                if modelo.ruta_archivo and os.path.exists(modelo.ruta_archivo):
                    os.remove(modelo.ruta_archivo)
                
                for archivo_config in modelo.archivos_config:
                    if archivo_config.ruta_archivo and os.path.exists(archivo_config.ruta_archivo):
                        os.remove(archivo_config.ruta_archivo)
                
                db.session.delete(modelo)

            dispositivos_usuario = Dispositivo.query.filter_by(usuario_id=user_id).all()
            for dispositivo in dispositivos_usuario:
                db.session.delete(dispositivo)

            db.session.delete(user)
            db.session.commit()

            session.clear()
            flash("Tu cuenta y todos tus datos han sido eliminados permanentemente.", "success")
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar la cuenta: {str(e)}", "error")
            return redirect(url_for('cuenta.index'))

    return redirect(url_for('auth.login'))