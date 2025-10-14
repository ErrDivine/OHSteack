from app.models import User


def register(client, username='member', email='member@example.com', password='Secret123'):
    return client.post(
        '/auth/register',
        data={
            'username': username,
            'email': email,
            'full_name': 'Test Member',
            'password': password,
            'password_confirm': password,
        },
        follow_redirects=True,
    )


def login(client, login_value='member', password='Secret123'):
    return client.post(
        '/auth/login',
        data={
            'login': login_value,
            'password': password,
        },
        follow_redirects=True,
    )


def test_register_creates_user_and_logs_in(client, app):
    response = register(client)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert '_user_id' in sess

    with app.app_context():
        user = User.query.filter_by(username='member').first()
        assert user is not None
        assert user.email == 'member@example.com'


def test_login_with_username_and_logout(client, app):
    register(client)
    client.get('/auth/logout', follow_redirects=True)

    response = login(client)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('_user_id') is not None

    # logout clears the session
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert '_user_id' not in sess
