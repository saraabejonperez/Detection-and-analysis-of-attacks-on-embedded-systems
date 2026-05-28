def test_acceso_admin_denegado_usuario_normal(client):
    """Prueba que un usuario SIN privilegios es expulsado del panel de administración"""
    
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
    """Prueba que un usuario CON privilegios sí puede ver el panel"""
    
    with client.session_transaction() as sess:
        sess['user_id'] = 99
        sess['username'] = 'super_admin'
        sess['is_admin'] = True

    response = client.get('/admin/usuarios')
    html_respuesta = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Gestión de Usuarios" in html_respuesta