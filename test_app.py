import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_users():
    # Reset users data before each test
    from app import users
    users.clear()
    users.extend([
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ])

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Welcome to Flask API"

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "healthy"

def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert len(data['users']) == 2
    assert data['users'][0]['name'] == "Alice"

def test_get_user_by_id(client):
    response = client.get('/users/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['name'] == "Alice"
    assert data['email'] == "alice@example.com"

def test_get_user_not_found(client):
    response = client.get('/users/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == "User not found"

def test_create_user(client):
    new_user = {
        "name": "Charlie",
        "email": "charlie@example.com"
    }
    response = client.post('/users', 
                          data=json.dumps(new_user),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == "Charlie"
    assert data['email'] == "charlie@example.com"
    assert 'id' in data

def test_create_user_missing_fields(client):
    incomplete_user = {"name": "Charlie"}
    response = client.post('/users',
                          data=json.dumps(incomplete_user),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_update_user(client):
    updated_data = {
        "name": "Alice Updated",
        "email": "alice.updated@example.com"
    }
    response = client.put('/users/1',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == "Alice Updated"
    assert data['email'] == "alice.updated@example.com"

def test_update_user_partial(client):
    updated_data = {"name": "Alice Modified"}
    response = client.put('/users/1',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == "Alice Modified"
    assert data['email'] == "alice@example.com"

def test_update_user_not_found(client):
    updated_data = {"name": "Nobody"}
    response = client.put('/users/999',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 404

def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify user is deleted
    response = client.get('/users/1')
    assert response.status_code == 404

def test_delete_user_not_found(client):
    response = client.delete('/users/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
