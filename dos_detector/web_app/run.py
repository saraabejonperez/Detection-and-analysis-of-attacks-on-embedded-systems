from app import create_app
from werkzeug.security import generate_password_hash
from app.models import db, User
import getpass

app = create_app()

@app.cli.command("init-admin")
def init_admin():
    """
    Create an administrator user from the command line interface.
    """

    print("CREADOR DE USUARIOS ADMINISTRADORES")
    print(f'-'*35)
    username = input("\nNombre de usuario para el Admin: ")

    with app.app_context():
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            print("Error: Ese usuario ya existe.")
            return
        
    while True:
        password = getpass.getpass("Contraseña para el Admin: ")

        if len(password) < 8:
            print("Error: La contraseña debe tener al menos 8 caracteres. Inténtelo de nuevo.")
            continue

        confirm_password = getpass.getpass("Confirmación de contraseña: ")
        
        if password != confirm_password:
            print("Error: Las contraseñas no coinciden. Inténtelo de nuevo.\n")
            continue

        break

    password_hash = generate_password_hash(password)
    admin_user = User(username=username, password_hash=password_hash, is_admin=True)
    
    db.session.add(admin_user)
    db.session.commit()
    print(f"\nSe ha creado un usuario administrador: {username}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)