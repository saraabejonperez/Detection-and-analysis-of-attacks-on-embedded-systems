from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    # Si el usuario ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template("index.html")