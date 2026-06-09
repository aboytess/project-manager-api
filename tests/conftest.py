import pytest
from app import create_app
from app.extensions import db as _db
from app.config import TestingConfig


@pytest.fixture()
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def registered_user(client):
    resp = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    return resp.get_json()


@pytest.fixture()
def auth_headers(registered_user):
    return {'Authorization': f'Bearer {registered_user["access_token"]}'}


@pytest.fixture()
def second_user(client):
    resp = client.post('/api/auth/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'password123'
    })
    return resp.get_json()


@pytest.fixture()
def second_auth_headers(second_user):
    return {'Authorization': f'Bearer {second_user["access_token"]}'}


@pytest.fixture()
def project(client, auth_headers):
    resp = client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'A test project'
    }, headers=auth_headers)
    return resp.get_json()
