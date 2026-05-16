import requests
import subprocess
import time
import os
import signal
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:5000"
PYTHON_EXE = "./venv/bin/python"
APP_SCRIPT = "src/app/main.py"

def run_test():
    # 1. Start the Flask app in the background
    print("Starting Flask app...")
    process = subprocess.Popen([PYTHON_EXE, APP_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Give it some time to start
    time.sleep(5)
    
    # Check if the app is up
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("Flask app is up and running!")
        else:
            print(f"Flask app failed to start! Status: {response.status_code}")
            return
    except Exception as e:
        print(f"Could not connect to Flask app: {e}")
        return

    try:
        # 2. Test /api/import-repeaters
        print("\nTesting /api/import-repeaters...")
        
        # Sample BTECH format content (CSV)
        # Note: using the column names that the parser expects
        btech_content = "name,rx_freq_hz,tx_freq_hz,tx_sub_audio_hz,rx_sub_audio_hz,scan,tx_power\nExisting,147.88,146.55,1000,1000,1,M"
        
        payload = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "current_content": btech_content
        }
        
        response = requests.post(f"{API_BASE_URL}/api/import-repeaters", json=payload)
        
        if response.status_code != 200:
            print(f"Error in /api/import-repeaters: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        print("Response from /api/import-repeaters received.")
        print(f"Action: {data.get('action')}")
        print(f"Found {len(data.get('repeaters', []))} new repeaters.")
        print(f"Existing channels: {len(data.get('existing_channels', []))}")

        # 3. Test /api/apply-import
        print("\nTesting /api/apply-import...")
        
        # We will 'pin' the existing channel (index 0) and add one of the new repeaters
        apply_payload = {
            "pinned_indices": [0],
            "new_repeaters": [],
            "current_content": btech_content
        }
        if data.get('repeaters'):
            apply_payload["new_repeaters"] = [data['repeaters'][0]]
            print(f"Adding repeater: {apply_payload['new_repeaters'][0].get('n')}")

        response = requests.post(f"{API_BASE_URL}/api/apply-import", json=apply_payload)
        
        if response.status_code != 200:
            print(f"Error in /api/apply-import: {response.status_code} - {response.text}")
            return
        
        apply_data = response.json()
        print("Response from /api/apply-import received.")
        print(f"Status: {apply_data.get('status')}")
        
        output_content = apply_data.get('content', '')
        print("\n--- Resulting Content ---")
        print(format_output(output_content))
        print("--------------------------")
        
        # 4. Verification of frequencies
        # We expect the existing channel to have 147.88 MHz and 146.55 MHz
        # Note: The output format might be BTECH CSV or Clipboard JSON
        
        found_147 = "147.88" in output_content
        found_146 = "146.55" in output_content
        
        if found_147 and found_146:
            print("\nSUCCESS: Existing channel frequencies preserved correctly.")
        else:
            print("\nFAILURE: Existing channel frequencies corrupted!")
            if not found_147:
                print("  Missing 1rad7.88")
            if not found_146:
                print("  Missing 146.55")

        # Check if the new repeater was added (it should be in the output)
        if apply_payload["new_repeaters"] and apply_payload["new_repeaters"][0].get('n') in output_content:
            print(f"SUCCESS: New repeater '{apply_payload['new_repeaters'][0].get('n')}' added successfully.")
        else:
            print(f"FAILURE: New repeater '{apply_payload['new_repeaters'][0].get('n') if apply_payload['new_repeaters'] else 'N/A'}' not found in output!")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up: Stopping Flask app...")
        process.terminate()
        process.wait()
        print("Flask app stopped.")

def format_output(content):
    if len(content) > 500:
        return content[:500] + "... [truncated]"
    return content

if __name__ == "__main__":
    run_test()
