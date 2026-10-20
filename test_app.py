import pytest

from fastapi.testclient import TestClient
from app_final import app


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as e:
        yield e


def test_health(client):
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_version(client):
    response = client.get('/version')

    assert response.status_code == 200
    assert 'version' in response.json()


def test_root(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json()['message'] == 'Приложение работает'


def test_categorize_transport(client):
    response = client.post('/categorize', json={'description': 'такси до дома'})

    assert response.status_code == 200
    assert response.json()['category'] == 'транспорт'
    assert response.json()['confidence'] > 0


def test_categorize_empty_description(client):
    response = client.post('/categorize', json={'description': ''})

    assert response.status_code == 422


def test_batch_limit(client):
    response = client.post('/categorize/batch',
                           json={'descriptions': ['такси', 'майбах', 'бмв', 'хёндай', 'ауди', 'худи', 'порш', 'китаец',
                                                  'вольва', 'мини', 'аурус']})

    assert response.status_code == 400
    assert 'detail' in response.json()
