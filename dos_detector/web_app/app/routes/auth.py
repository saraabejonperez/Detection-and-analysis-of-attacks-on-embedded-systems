import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Nombre de usuario no válido. Ya está en uso.", "error")
            return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session.permanent = False
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Nombre de usuario o contraseña erróneos.", "error")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/guest")
def guest():
    session.clear()
    session.permanent = False
    session['guest'] = True
    session['guest_models'] = []
    session['guest_devices'] = []
    return redirect(url_for("dashboard.dashboard"))

@auth_bp.route("/logout")
def logout():
    if session.get('guest') and 'guest_models' in session:
        for modelo in session['guest_models']:
            file_path = modelo.get('ruta_archivo')
            features_path = modelo.get('ruta_features')
            
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error borrando archivo invitado: {e}")
            
            if features_path and os.path.exists(features_path):
                try:
                    os.remove(features_path)
                except Exception as e:
                    print(f"Error borrando features invitado: {e}")
                    
    session.clear()
    session.permanent = False
    return redirect(url_for("main.index"))