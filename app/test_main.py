import pytest
from main import app, tasks

@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()
    yield
    tasks.clear()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_intentional_failure():
    assert 1 == 2, "This will fail and block the deploy"

def test_index(client):
    r = client.get('/')
    assert r.status_code == 200
    assert r.get_json()['app'] == 'Ship It'

def test_create_task(client):
    r = client.post('/tasks', json={'title': 'Write Dockerfile'})
    assert r.status_code == 201
    assert r.get_json()['title'] == 'Write Dockerfile'

def test_get_tasks(client):
    client.post('/tasks', json={'title': 'Task A'})
    r = client.get('/tasks')
    assert r.status_code == 200
    assert len(r.get_json()) == 1

def test_delete_task(client):
    r = client.post('/tasks', json={'title': 'To delete'})
    task_id = r.get_json()['id']
    r = client.delete(f'/tasks/{task_id}')
    assert r.status_code == 200

def test_delete_missing_task(client):
    r = client.delete('/tasks/999')
    assert r.status_code == 404

def test_create_task_missing_title(client):
    r = client.post('/tasks', json={})
    assert r.status_code == 400

def test_healthz(client):
    r = client.get('/healthz')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'
