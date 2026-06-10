def test_pagina_inicio_carga_bien(client):
    """
    Test that the application's landing page loads correctly.

    :param client: The Werkzeug test client used to simulate the HTTP request.
    :type client: FlaskClient
    :return: None. The test relies entirely on assert statements.
    :rtype: None
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'DoS Detection System' in response.data


def test_acceso_invitado(client):
    """
    Test the guest authentication flow and dashboard redirection.

    :param client: The Werkzeug test client used to simulate the HTTP request.
    :type client: FlaskClient
    :return: None. The test relies entirely on assert statements.
    :rtype: None
    """
    response = client.get('/auth/guest')
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']
    response_dashboard = client.get('/dashboard/', follow_redirects=True)
    assert response_dashboard.status_code == 200