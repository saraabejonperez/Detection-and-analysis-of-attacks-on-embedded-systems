from flask import Blueprint, render_template, session, redirect, url_for


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Render the application's landing page or redirect authenticated users.

    :return: A redirect response to the dashboard if the user is logged in, 
             otherwise the rendered HTML string for the index page.
    :rtype: str | Response
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template("index.html")