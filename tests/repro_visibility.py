from playwright.sync_api import expect
import pytest
import subprocess
import time
import os

BASE_URL = "http://localhost:5001/"

@pytest.fixture(scope="module")
def server():
    # Start the flask server in a subprocess
    # We need to make far sure it's running before the tests start.
    cwd = "/home/nchilton/repos/chirp2uvpro/src/app"
    env = os.environ.copy()
    env["FLASK_APP"] = "main.py"
    
    proc = subprocess.Popen(["python", "-m", "flask", "run", "--port=5001"], 
                             cwd=cwd,
                             env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3) # Wait for server to start
    yield proc
    proc.terminate()

def test_repro_visibility(page, server):
    page.goto(BASE_URL)
    
    print("Checking visibility of textarea before click")
    textarea = page.locator('textarea[name="content"]')
    
    print("Clicking #text-tab")
    page.click("#text-tab")
    
    print("Checking visibility of textarea after click")
    # expect has built-in retry logic
    expect(textarea).to_be_visible()
    
    print("Filling textarea")
    page.fill('textarea[name="content"]', "test content")
    
    print("Test passed!")
