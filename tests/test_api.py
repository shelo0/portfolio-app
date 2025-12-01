import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'healthy'

def test_get_profile(client):
    r = client.get('/api/profile')
    assert r.status_code == 200

def test_get_skills(client):
    r = client.get('/api/skills')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

def test_create_skill(client):
    r = client.post('/api/skills', json={'name': 'Test', 'category': 'Test', 'proficiency': 75})
    assert r.status_code == 201

def test_get_projects(client):
    r = client.get('/api/projects')
    assert r.status_code == 200

def test_create_project(client):
    r = client.post('/api/projects', json={'title': 'Test Project', 'description': 'Test'})
    assert r.status_code == 201

def test_send_message(client):
    r = client.post('/api/messages', json={'name': 'Test', 'email': 'test@test.com', 'message': 'Hello'})
    assert r.status_code == 201

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
