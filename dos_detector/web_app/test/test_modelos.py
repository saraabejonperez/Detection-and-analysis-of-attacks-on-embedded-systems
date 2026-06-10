import io


def test_subida_extension_invalida(client):
    """
    Test that the system rejects file uploads with invalid extensions.

    :param client: The Werkzeug test client used to simulate the HTTP request.
    :type client: FlaskClient
    :return: None. The test relies entirely on assert statements.
    :rtype: None
    """
    client.get('/auth/guest')
    
    datos_formulario = {
        'archivo_modelo': (io.BytesIO(b"contenido falso"), 'virus.txt'),
        'archivo_features': (io.BytesIO(b"config falsa"), 'features.npy')
    }
    
    response = client.post(
        '/modelos/upload', 
        data=datos_formulario, 
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    html_respuesta = response.data.decode('utf-8')
    assert "Formato de modelo no válido" in html_respuesta
    assert "Solo se permiten archivos .pkl" in html_respuesta


def test_subida_falta_archivo(client):
    """
    Test that the upload process is rejected if a required file is missing.

    :param client: The Werkzeug test client used to simulate the HTTP request.
    :type client: FlaskClient
    :return: None. The test relies entirely on assert statements.
    :rtype: None
    """
    client.get('/auth/guest')
    
    datos_formulario = {
        'archivo_modelo': (io.BytesIO(b"contenido falso"), 'modelo.pkl')
    }
    
    response = client.post(
        '/modelos/upload', 
        data=datos_formulario, 
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    html_respuesta = response.data.decode('utf-8')
    assert "Faltan archivos requeridos" in html_respuesta