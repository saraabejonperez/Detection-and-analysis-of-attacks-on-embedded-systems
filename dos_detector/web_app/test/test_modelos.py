import io

def test_subida_extension_invalida(client):
    """Prueba que el sistema rechaza archivos que no sean .pkl o .npy"""
    
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
    """Prueba que el sistema rechaza la subida si falta uno de los dos archivos"""
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