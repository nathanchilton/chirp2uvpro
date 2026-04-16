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
        'content': 'title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nTest,146520000,146520000,0,0,M,25000,0,0,0,0,0,0,0,FM,FM',
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

def test_api_upload_success():
    """
    Test POST /api/convert/upload with a valid CSV file
    """
    with open("test_upload.csv", "rb") as f:
        files = {"file": ("test_upload.csv", f, "text/csv")}
        response = requests.post(f"{BASE_URL}/api/convert/upload", files=files)
    
    print(f"Response text: {response.text}")
    assert response.status_code == 200
    assert "uploaded and converted successfully!" in response.text
    assert 'role="textbox"' in response.text

