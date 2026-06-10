def test_acceso_admin_denegado_usuario_normal(client):
    """
    Test that a user without administrator privileges is denied access to the admin panel.

    :param client: The Werkzeug test client used to simulate the HTTP request.
    :type client: FlaskClient
    :return: None. The test relies entirely on assert statements.
    :rtype: None
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test_user'
        sess['is_admin'] = False

    response = client.get('/admin/usuarios', follow_redirects=True)
    html_respuesta = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Acceso denegado. Se requieren permisos de administrador" in html_respuesta
    assert "Gestión de Usuarios" not in html_respuesta


def test_acceso_admin_permitido(client):
    """
    Test that a user with administrator privileges is successfully granted access.

    :param client: The Werkzeug test client used to simulate the HTTP request.
    :type client: FlaskClient
    :return: None. The test relies entirely on assert statements.
    :rtype: None
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 99
        sess['username'] = 'super_admin'
        sess['is_admin'] = True

    response = client.get('/admin/usuarios')
    html_respuesta = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Gestión de Usuarios" in html_respuesta