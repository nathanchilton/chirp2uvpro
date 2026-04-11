import pytest
import os
import sqlite3
import subprocess
import time
from playwright.sync_api import Page, expect

TEST_PORT = 5001
BASE_URL = f"http://localhost:{TEST_PORT}"
DB_PATH = "src/database/app.db"

@pytest.fixture(scope="session", autouse=True)
def server():
    """
    Fixture to start the Flask server before running tests and stop it after.
    """
    env = os.environ.copy()
    env["FLASK_APP"] = "src.app.main:app"
    env["PYTHONPATH"] = os.getcwd()
    process = subprocess.Popen(["./venv/bin/python", "-m", "flask", "run", f"--port={TEST_PORT}"], env=env)
    
    timeout = 15
    start_time = time.time()
    while True:
        try:
            import urllib.request
            urllib.request.urlopen(f"{BASE_URL}/health")
            break
        except Exception:
            if time.time() - start_time > timeout:
                raise RuntimeError("Server failed to start within timeout")
            time.sleep(0.5)
    
    yield process
    
    process.terminate()
    process.wait()

@pytest.fixture
def clear_db():
    """
    Fixture to clear the conversion_history table before each test.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversion_history")
    conn.commit()
    conn.close()
    yield
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversion_history")
    conn.commit()
    conn.close()

def test_database_persistence_file_upload(page: Page, clear_db):
    """
    Test case: File upload -> database entry
    """
    # 1. Prepare a dummy CSV file
    test_file_path = "tests/integration/test_upload.csv"
    with open(test_file_path, "w") as f:
        f.write("column1,column2\nvalue1,value2")

    try:
        # 2. Perform upload via Playwright
        page.goto(BASE_URL)
        page.click('button[id="upload-tab"]')
        # Wait for the upload content to load via hx-get
        expect(page.locator("#upload-content")).to_contain_text("Select CSV file")
        page.set_input_files('input[type="file"]', test_file_path)
        page.click('button[id="upload-button"]')
        # Wait for the upload to complete and result to be displayed
        expect(page.locator("#upload-result")).to_contain_text("successfully")



        # 3. Verify database entry
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM conversion_history WHERE input_filename LIKE '%test_upload.csv'")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1, f"Expected 1 database entry for file upload, found {count}"
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_database_persistence_text_paste(page: Page, clear_db):
    """
    Test case: Text paste -> database entry
    """
    # 1. Perform paste via Playwright
    page.goto(BASE_URL)
    csv_content = "column1,column2\nvalue1,value2"
    page.fill('textarea[name="csv_content"]', csv_content)
    page.click('button[id="convert-button"]')
    # Wait for the paste to complete and result to be displayed
    expect(page.locator("#result")).to_contain_text("successful!")





    # 2. Verify database entry
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM conversion_history WHERE input_filename = 'pasted_content'")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1, f"Expected 1 database entry for text paste, found {count}"
