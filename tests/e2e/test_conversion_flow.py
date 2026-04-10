import pytest
import os
import subprocess
import time
from playwright.sync_api import Page, expect

TEST_PORT = 5001
BASE_URL = f"http://localhost:{TEST_PORT}"

@pytest.fixture(scope="session", autouse=True)
def server():
    """
    Fixture to start the Flask server before running tests and stop it after.
    """
    # Start the server in a subprocess
    env = os.environ.copy()
    env["FLASK_APP"] = "src.app.main:app"
    env["PYTHONPATH"] = os.getcwd()
    process = subprocess.Popen(["python3", "-m", "flask", "run", f"--port={TEST_PORT}"], env=env)
    
    # Wait for the server to be ready
    timeout = 15
    start_time = time.time()
    while True:
        try:
            # Try to connect to the server
            import urllib.request
            urllib.request.urlopen(f"{BASE_URL}/health")
            break
        except Exception:
            if time.time() - start_time > timeout:
                raise RuntimeError("Server failed to start within timeout")
            time.sleep(0.5)
    
    yield process
    
    # Shutdown the server
    process.terminate()
    process.wait()

def test_conversion_flow_paste_chirp_to_btech(page: Page):
    """
    Test the full conversion flow using the paste method (CHIRP -> BTECH).
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)
    
    # 2. Verify initial state (CHIRP mode)
    expect(page.locator(".converter-title")).to_contain_text("Convert CSV Content")
    
    # 3. Prepare sample CHIRP content
    chirp_content = "Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM\n2,Test2,146.550,0,None,None,0,FM"
    
    # 4. Paste content into the textarea
    page.fill('textarea[name="csv_content"]', chirp_content)
    
    # 5. Click the Convert button
    page.click("#convert-button")
    
    # 6. Wait for the result to appear and verify it
    result_locator = page.locator("#result")
    expect(result_locator).not_to_contain_text("Result will appear here.")
    
    # 7. Check if the success alert is present
    expect(page.locator(".alert-success")).to_be_visible()

