import pytest
from src.app.main import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_import_repeaters_success(client):
    payload = {'latitude': 45.0, 'longitude': -93.0}
    response = client.post('/api/import-repeaters', 
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['repeaters']) == 30
    # Check that the first repeater has the expected structure
    repeater = data['repeaters'][0]
    assert 'n' in repeater
    assert 'rf' in repeater
    assert 'tf' in repeater
    assert 'ts' in repeater
    assert 'rs' in repeater
    # Verify sub-audio is within a valid CTCSS range (67.0 - 250.0 Hz)
    assert 67.0 <= repeater['ts'] <= 250.0
    assert 67.0 <= repeater['rs'] <= 250.0

def test_import_repeaters_missing_data(client):
    payload = {'latitude': 45.0}
    response = client.post('/api/import-repeaters', 
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Missing latitude or longitude' in data['error']

def test_import_repeaters_invalid_json(client):
    response = client.post('/api/import-repeaters', 
                           data="not a json",
                           content_type='application/json')
    assert response.status_code == 400
