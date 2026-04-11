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
    process = subprocess.Popen(["./venv/bin/python", "-m", "flask", "run", f"--port={TEST_PORT}"], env=
                               env)
    
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

def test_history_display_empty(page: Page, clear_db):
    """
    Test that the empty state message is displayed when no history exists.
    """
    page.goto(BASE_URL)
    # Check for the empty state message in the history fragment
    empty_state_locator = page.locator(".history-list .text-muted.italic")
    expect(empty_state_locator).to_contain_text("No conversion history found.")

def test_history_display_with_records(page: Page, clear_db):
    """
    Test that conversion history items are displayed when they exist.
    """
    # 1. Insert a dummy record into the database
    conn = sqlite3.connect('src/database/app.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversion_history (input_filename, output_filename, status, warning) VALUES (?, ?, ?, ?)",
        ("test_orig.csv", "test_conv.csv", "success", None)
    )
    conn.commit()
    conn.close()

    # 2. Navigate to the application
    page.goto(BASE_URL)

    # 3. Verify the history item is displayed
    history_item = page.locator(".history-list .list-group-item")
    expect(history_item).to_be_visible()
    expect(history_item).to_contain_text("test_orig.csv")
    expect(history_item).to_contain_text("test_conv.csv")
    expect(history_item).to_contain_text("success")

