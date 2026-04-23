import pytest
import os
import sqlite3
import subprocess
import time
from tests.integration.config import TEST_PORT, BASE_URL, DB_PATH

@pytest.fixture(scope="session", autouse=
               True)
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
