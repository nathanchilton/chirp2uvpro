import pytest
from src.app.main import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_set_location_success(client):
    payload = {'latitude': 45.0, 'longitude': -93.0}
    response = client.post('/api/location', 
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert '45.0' in data['message']
    assert '-93.0' in data['message']

def test_set_location_missing_data(client):
    payload = {'latitude': 45.0}
    response = client.post('/api/location', 
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Missing latitude or longitude' in data['error']

def test_set_location_invalid_json(client):
    response = client.post('/api/location', 
                           data="not a json",
                           content_type='application/json')
    # Flask might return 400 for invalid JSON
    assert response.status_code == 400
