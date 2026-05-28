def test_pagina_inicio_carga_bien(client):
    """Prueba que la página principal devuelve un estado 200 (OK)"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'DoS Detection System' in response.data

def test_acceso_invitado(client):
    """Prueba que al entrar como invitado, se crea la sesión y te redirige al dashboard"""
    response = client.get('/auth/guest')
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']
    response_dashboard = client.get('/dashboard/', follow_redirects=True)
    assert response_dashboard.status_code == 200