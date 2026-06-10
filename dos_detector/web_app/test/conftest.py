import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.models import db, User

@pytest.fixture
def app():
    """
    Create and configure a fresh Flask application instance for testing.

    It yields the application context, and upon test completion, 
    safely tears down the database.

    :return: A generator yielding the configured Flask application instance.
    :rtype: Generator[Flask, None, None]
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Provide a Werkzeug test client to simulate HTTP requests.

    :param app: The Flask application instance provided by the `app` fixture.
    :type app: Flask
    :return: The test client capable of executing simulated requests.
    :rtype: FlaskClient
    """
    return app.test_client()


@pytest.fixture
def init_database(app):
    """
    Seed the in-memory test database with initial mock data.

    This fixture creates a standard dummy user with fake credentials 
    and commits it to the database before the tests run.

    :param app: The Flask application instance provided by the `app` fixture.
    :type app: Flask
    :return: The SQLAlchemy database object containing the seeded data.
    :rtype: SQLAlchemy
    """
    usuario_prueba = User(username="test_user", password_hash="hash_falso", is_admin=False)
    db.session.add(usuario_prueba)
    db.session.commit()
    return db