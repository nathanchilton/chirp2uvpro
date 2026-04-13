import pytest
import requests
from tests.integration.config import BASE_URL

def test_api_paste_400_no_content():
    """
    Test POST /api/convert/paste with no content
    """
    data = {"direction": "chirp_to_btech"}
    response = requests.post(f"{BASE_URL}/api/convert/paste", json=data)
    assert response.status_code == 400
    assert "No content provided" in response.text

def test_api_paste_400_invalid_direction():
    """
    Test POST /api/convert/paste with invalid direction
    """
    data = {"content": "some content", "direction": "invalid_direction"}
    response = requests.post(f"{BASE_URL}/api/convert/paste", json=data)
    assert response.status_code == 400
    assert "Invalid direction" in response.text

def test_api_paste_form_encoded_chirp_to_btech():
    """
    Test POST /api/convert/paste with form-encoded data (chirp_to_btech)
    """
    data = {
        'content': 'Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM',
        'direction': 'chirp_to_btech'
    }
    response = requests.post(f"{BASE_URL}/api/convert/paste", data=data)
    assert response.status_code == 200
    assert "uploaded and converted successfully!" in response.text

def test_api_paste_form_encoded_btech_to_chirp():
    """
    Test POST /api/convert/paste with form-encoded data (btech_to_chirp)
    """
    data = {
        'content': 'BTECH UV{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}',
        'direction': 'btech_to_chirp'
    }
    response = requests.post(f"{BASE_URL}/api/convert/paste", data=data)
    assert response.status_code == 200
    assert "uploaded and converted to chirp" in response.text.lower() or "uploaded and converted successfully!" in response.text

def test_api_paste_json_valid():
    """
    Test POST /api/convert/paste with JSON payload (valid)
    """
    data = {
        'content': 'Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM',
        'direction': 'chirp_to_btech'
    }
    response = requests.post(f"{BASE_URL}/api/convert/paste", json=data)
    assert response.status_code == 200
    assert "uploaded and converted successfully!" in response.text
