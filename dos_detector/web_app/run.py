from app import create_app

app = create_app()

from werkzeug.security import generate_password_hash
from app.models import db, User

@app.cli.command("init-admin")
def init_admin():
    """Crea un usuario administrador inicial desde la terminal"""
    print("--- CREADOR DE ADMINISTRADOR INICIAL ---")
    username = input("Nombre de usuario para el Admin: ")
    password = input("Contraseña para el Admin: ")
    
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        print("Error: Ese usuario ya existe.")
        return
        
    if len(password) < 8:
        print("Error: La contraseña debe tener al menos 8 caracteres.")
        return

    password_hash = generate_password_hash(password)
    admin_user = User(username=username, password_hash=password_hash, is_admin=True)
    
    db.session.add(admin_user)
    db.session.commit()
    print(f"¡Éxito! El administrador '{username}' ha sido creado correctamente.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)