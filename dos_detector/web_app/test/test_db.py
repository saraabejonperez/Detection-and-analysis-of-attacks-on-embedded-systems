from app.models import db, User, Modelo, Dispositivo

def test_borrado_en_cascada(app, init_database):
    """Si se borra un usuario, sus modelos y dispositivos deben desaparecer de la BBDD"""
    
    with app.app_context():
        usuario = User.query.filter_by(username='test_user').first()

        nuevo_modelo = Modelo(nombre="test.pkl", ruta_archivo="/falsa", usuario=usuario)
        nuevo_disp = Dispositivo(nombre="m5stack_test", ip="192.168.1.1", usuario=usuario)

        db.session.add(nuevo_modelo)
        db.session.add(nuevo_disp)
        db.session.commit()

        assert Modelo.query.filter_by(usuario_id=usuario.id).count() == 1
        assert Dispositivo.query.filter_by(usuario_id=usuario.id).count() == 1

        db.session.delete(usuario)
        db.session.commit()

        assert Modelo.query.filter_by(usuario_id=usuario.id).count() == 0
        assert Dispositivo.query.filter_by(usuario_id=usuario.id).count() == 0