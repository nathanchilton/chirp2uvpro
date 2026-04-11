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
    expect(page.locator(".converter-title")).to_contain_text("Convert CHIRP to BTECH")
    
    # 3. Prepare sample CHIRP content
    chirp_content = "Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM\n2,Test2,146.550,0,None,None,0,FM"
    
    # 4. Paste content into the textarea
    page.fill('textarea[name="csv_content"]', chirp_content)
    
    # 5. Click the Convert button
    page.click("#convert-button")
    
    # 6. Wait for the result to appear and verify it
    result_locator = page.locator("#result").first
    expect(result_locator).to_contain_text("Conversion successful!", timeout=10000)
    
    # 7. Check if the success alert is present
    expect(page.locator(".alert-success")).to_be_visible()
    
    # 8. Verify the converted content (should be CHIRP format)
    # The converted content itself is NOT in the #result div,
    # but the #result div is updated with the success message.
    expect(result_locator).to_contain_text("Conversion successful!")
    
    # Check if the download link is present and has a correct filename
    download_link = page.locator('a[download^="converted_"]')
    expect(download_link).to_be_visible()
    download_filename = download_link.get_attribute("download")
    assert download_filename is not None
    assert download_filename.startswith("converted_")
    assert download_filename.endswith(".csv")

def test_conversion_flow_paste_btech_to_chirp(page: Page):
    """
    Test the full conversion flow using the paste method (BTECH -> CHIRP).
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)
    
    # 2. Switch to BTECH mode
    page.click("input[value='b2ch']")

    # 3. Prepare sample BTECH content
    btech_content = "1,Test,146.520,0,None,None,0,FM\n2,Test2,146.550,0,None,None,0,FM"

    # 4. Paste content into the textarea
    page.fill('textarea[name="csv_content"]', btech_content)

    # 5. Click the Convert button
    page.click("#convert-button")

    # 6. Wait for the result to appear and verify it
    result_locator = page.locator("#result").first
    expect(result_locator).to_contain_text("Conversion successful!", timeout=10000)

    # 7. Check if the success alert is present
    expect(page.locator(".alert-success")).to_be_visible()

    # 8. Verify the converted content (should be CHIRP format)
    # The converted content itself is NOT in the #result div,
    # but the #result div is updated with the success message.
    expect(result_locator).to_contain_text("Conversion successful!")

    # Check if the download link is present and has a correct filename
    download_link = page.locator('a[download^="converted_"]')
    expect(download_link).to_be_visible()
    download_filename = download_link.get_attribute("download")
    assert download_filename is not None
    assert download_filename.startswith("converted_")
    assert download_filename.endswith(".csv")
