from fastapi.testclient import TestClient
from app.main import app


def test_system_endpoints():
    with TestClient(app) as client:
        root = client.get('/')
        assert root.status_code == 200
        assert root.json()['release'] == 'master-e2e'
        assert client.get('/health').json()['status'] == 'ok'
        ready = client.get('/ready')
        assert ready.status_code == 200
        assert ready.json()['checks']['database'] is True
        response = client.get('/health', headers={'X-Request-ID':'phase3-test-id'})
        assert response.headers['X-Request-ID'] == 'phase3-test-id'
