from flask import Blueprint, render_template, session

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def dashboard():
    is_guest = session.get('guest', False)
    username = session.get('username', 'Invitado')
    
    return render_template("dashboard.html", username=username, is_guest=is_guest)