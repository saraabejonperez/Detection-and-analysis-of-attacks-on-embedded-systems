import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from ...models import db, User, Modelo, Dispositivo


admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    """
    Decorator to restrict route access to administrators only.

    It checks the active session for the 'is_admin' flag. If the 
    user is not an administrator, it flashes an error message and redirects 
    them to the main dashboard, preventing access to the decorated view.

    :param f: The view function to be decorated.
    :type f: Callable
    :return: The decorated function if the user is an admin, otherwise a redirect response.
    :rtype: Callable
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Acceso denegado. Se requieren permisos de administrador.", "error")
            return redirect(url_for('dashboard.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


@admin_bp.route("/admin/usuarios")
@admin_required
def gestion_usuarios():
    """
    Display the user management dashboard.

    This route retrieves all registered users from the database, excluding the 
    currently logged-in administrator, and passes them to the template for display.

    :return: The rendered HTML template for user management.
    :rtype: str
    """
    current_admin_id = session.get('user_id')
    usuarios = User.query.filter(User.id != current_admin_id).all()

    return render_template("admin_usuarios.html", usuarios=usuarios)


@admin_bp.route("/admin/usuarios/toggle_admin/<int:user_id>", methods=["POST"])
@admin_required
def toggle_admin(user_id: int):
    """
    Toggle the administrator privileges of a specific user.

    :param user_id: The unique identifier of the user.
    :type user_id: int
    :return: A redirect response back to the user management dashboard.
    :rtype: Response
    """
    usuario = User.query.get_or_404(user_id)
    
    usuario.is_admin = not usuario.is_admin
    db.session.commit()
    
    nuevo_rol = "Administrador" if usuario.is_admin else "Usuario normal"
    flash(f"Rol de '{usuario.username}' cambiado a {nuevo_rol}.", "success")
    return redirect(url_for('admin.gestion_usuarios'))


@admin_bp.route("/admin/usuarios/ver/<int:user_id>")
@admin_required
def ver_detalles(user_id: int):
    """
    Display detailed information for a specific user.

    :param user_id: Unique identifier of the user to inspect.
    :type user_id: int
    :return: The rendered HTML template showing user details.
    :rtype: str
    """
    usuario = User.query.get_or_404(user_id)
    return render_template("admin_ver_usuario.html", usuario=usuario)


@admin_bp.route("/admin/usuarios/delete/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id: int):
    """
    Delete a user and all their associated data from the database.

    :param user_id: Unique identifier of the user to delete.
    :type user_id: int
    :return: A redirect response back to the user management dashboard.
    :rtype: Response
    """
    usuario = User.query.get(user_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        flash(f"Usuario '{usuario.username}' y todos sus datos han sido eliminados.", "success")
    else:
        flash("Usuario no encontrado.", "error")
        
    return redirect(url_for('admin.gestion_usuarios'))


@admin_bp.route("/admin/modelos/delete/<int:model_id>", methods=["POST"])
@admin_required
def delete_model_admin(model_id: int):
    """
    Delete a model and its associated physical files.

    :param model_id: Unique identifier of the model to delete.
    :type model_id: int
    :return: A redirect response back to the owner's detailed view.
    :rtype: Response
    """
    modelo = Modelo.query.get_or_404(model_id)
    target_user_id = modelo.usuario_id
    
    if modelo.ruta_archivo and os.path.exists(modelo.ruta_archivo):
        os.remove(modelo.ruta_archivo)
        
    for archivo_config in modelo.archivos_config:
        if archivo_config.ruta_archivo and os.path.exists(archivo_config.ruta_archivo):
            os.remove(archivo_config.ruta_archivo)
            
    db.session.delete(modelo)
    db.session.commit()
    
    flash("Modelo e historial eliminados por el administrador.", "success")
    return redirect(url_for('admin.ver_detalles', user_id=target_user_id))


@admin_bp.route("/admin/dispositivos/delete/<int:device_id>", methods=["POST"])
@admin_required
def delete_device_admin(device_id: int):
    """
    Delete a device from the system.

    :param device_id: Unique identifier of the device to delete.
    :type device_id: int
    :return: A redirect response back to the owner's detailed view.
    :rtype: Response
    """
    dispositivo = Dispositivo.query.get_or_404(device_id)
    target_user_id = dispositivo.usuario_id
    
    db.session.delete(dispositivo)
    db.session.commit()
    
    flash("Dispositivo desvinculado por el administrador.", "success")
    return redirect(url_for('admin.ver_detalles', user_id=target_user_id))