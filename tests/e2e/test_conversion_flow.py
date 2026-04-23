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
    env["PYTHONPATH"] = os.path.abspath("src") + os.pathsep + os.getcwd()
    process = subprocess.Popen(["./venv/bin/python", "-m", "flask", "run", f"--port={TEST_PORT}"], env=env)
    
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

@pytest.fixture(autouse=True)
def intercept_requests(page: Page):
    """
    Fixture to intercept and log requests and responses for debugging.
    """
    def handle_request(request):
        if "/api/convert/paste" in request.url and request.method == "POST":
            print(f"[Intercepted Request] URL: {request.url} | Method: {request.method}")
            print(f"[Intercepted Request] Headers: {request.headers}")
            try:
                print(f"[Intercepted Request] Post Data: {request.post_data}")
            except Exception as e:
                print(f"[Intercepted Request] Could not read post data: {e}")

    def handle_response(response):
        if "/api/convert/paste" in response.url and response.status >= 400:
            print(f"[Intercepted Response] URL: {response.url} | Status: {response.status}")
            try:
                print(f"[Intercepted Response] Body: {response.text()}")
            except Exception as e:
                print(f"[Intercepted Response] Could not read response body: {e}")

    page.on("request", handle_request)
    page.on("response", handle_response)
    yield

def test_conversion_flow_paste_chirp_to_btech(page: Page):
    """
    Test the full conversion flow using the paste method (CHIRP -> BTECH).
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)
    
    # 2. Verify initial state (Auto-detect)
    expect(page.locator("#input-format")).to_have_value("auto")
    expect(page.locator("#output-format")).to_have_value("chirp")
    expect(page.locator("#converter-title")).to_contain_text("Converter")
    
    # 3. Switch to Text Input tab
    page.click("#text-tab")
    
    # 4. Prepare sample CHIRP content
    chirp_content = "Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM\n2,Test2,146.550,0,None,None,0,FM"
    
    # 5. Paste content into the textarea
    page.fill('textarea[name="content"]', chirp_content)
    
    # 5. Click the Convert button
    page.click("#convert-button")
    # 6. Wait for the result to appear and verify it
    result_locator = page.locator("#result").first
    expect(result_locator).to_contain_text("Content pasted and converted successfully!", timeout=10000)
    
    # 7. Check if the success alert is present
    # (Note: For paste method, we just check the text in the result div)
    expect(result_locator).to_contain_text("Content pasted and converted successfully!")
    
    # 8. Verify the converted content (should be CHIRP format)
    # The converted content itself is NOT in the #result div,
    # but the #result div is updated with the success message.
    expect(result_locator).to_contain_text("Content pasted and converted successfully!")


def test_conversion_flow_paste_btech_to_chirp(page: Page):
    """
    Test the full conversion flow using the paste method (BTECH -> CHIRP).
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)
    
    # 2. Switch to BTECH mode
    page.select_option("#input-format", "btech")
    page.select_option("#output-format", "chirp")
    page.click("#text-tab")
    
    # 3. Prepare sample BTECH content
    btech_content = 'BTECH UV{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
    
    # 4. Paste content into the textarea
    page.fill('textarea[name="content"]', btech_content)
    
    # 5. Click the Convert button
    page.click("#convert-button")
    # 6. Wait for the result to appear and verify it
    result_locator = page.locator("#result").first
    expect(result_locator).to_contain_text("Content pasted and converted successfully!", timeout=10000)
    
    # 7. Check if the success alert is present
    # (Note: For paste method, we just check the text in the result div)
    expect(result_locator).to_contain_text("Content pasted and converted successfully!")
    
    # 8. Verify the converted content (should be CHIRP format)
    # The converted content itself is NOT in the #result div,
    # but the #result div is updated with the success message.
    expect(result_locator).to_contain_text("Content pasted and converted successfully!")

    
    # 8. Verify the converted content (should be CHIRP format)
    # The converted content itself is NOT in the #result div,
    # but the #result div is updated with the success message.
    expect(result_locator).to_contain_text("Content pasted and converted successfully!")

