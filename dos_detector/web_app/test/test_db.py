from app.models import db, User, Modelo, Dispositivo

def test_borrado_en_cascada(app, init_database):
    """
    Test the SQLAlchemy cascading delete behavior for user records.

    :param app: The initialized Flask application instance provided by the fixture.
    :type app: Flask
    :param init_database: The SQLAlchemy database object containing the seeded test user.
    :type init_database: SQLAlchemy
    :return: None. The test relies entirely on database query assert statements.
    :rtype: None
    """
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