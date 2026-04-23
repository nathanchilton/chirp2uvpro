import requests
import sys
import re

BASE_URL = "http://localhost:5000/api/convert"

def extract_textarea_content(html):
    match = re.search(r'<textarea.*?>(.*?)</textarea>', html, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "No textarea content found"

def test_different_outputs():
    content = "Channel,Name,frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM"
    
    print("--- Testing BTECH output ---")
    data_btech = {"content": content, "input_format": "chirp", "output_format": "btech"}
    response = requests.post(f"{BASE_URL}/paste", json=data_btech)
    print(f"Status: {response.status_code}")
    textarea_content = extract_textarea_content(response.text)
    print(f"Textarea Content:\n{textarea_content}")

    print("\n--- Testing CHIRP output ---")
    data_chirp = {"content": content, "input_format": "chirp", "output_format": "chirp"}
    response = requests.post(f"{BASE_URL}/paste", json=data_chirp)
    print(f"Status: {response.status_code}")
    textarea_content = extract_textarea_content(response.text)
    print(f"Textarea Content:\n{textarea_content}")

if __name__ == "__main__":
    test_different_outputs()

