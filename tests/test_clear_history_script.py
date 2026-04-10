import os
import sqlite3
import uuid
from flask import Flask
from src.app.api.routes import api_bp
from database import init_db

def test_clear_history():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.config['TESTING'] = True
    
    # Use a temporary database for testing if possible, 
    # but for now, we'll use the existing one and clean up after.
    # In a real scenario, we'd use a separate test DB.
    
    client = app.test_client()
    
    # 1. Setup: Create a dummy file in uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'app', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    dummy_filename = "test_file.csv"
    dummy_path = os.path.join(UPLOAD_FOLDER, dummy_filename)
    with open(dummy_path, 'w') as f:
        f.write("column1,column2\nvalue1,value2")
    
    # 2. Add entry to database manually to simulate an upload
    conn = sqlite3.connect('src/database/app.db') # Using the actual app.db path
    try:
        with conn:
            conn.execute('INSERT INTO uploaded_files (filename, file_path) VALUES (?, ?)', (dummy_filename, dummy_path))
            conn.execute('INSERT INTO conversion_history (input_filename, output_filename, status, warning) VALUES (?, ?, ?, ?)', 
                         (dummy_filename, 'dummy_output.csv', 'success', ''))
        
        print(f"Test setup complete. Dummy file created at: {dummy_path}")
        
        # 3. Trigger clear_history
        print("Triggering /history/clear...")
        response = client.post('/history/clear')
        
        # 4. Verify results
        if response.status_code == 204:
            print("Route returned 204 (Success)")
        else:
            print(f"Route returned {response.status_code}: {response.data.decode()}")

        file_exists = os.path.exists(dummy_path)
        print(f"File exists after clear: {file_exists}")
        
        # Check DB
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM uploaded_files')
        db_count = cursor.fetchone()[0]
        print(f"Database uploaded_files count: {db_count}")
        
        if not file_exists and db_count == 0:
            print("SUCCESS: History and files cleared.")
        else:
            print("FAILURE: History or files remained.")
            
    except Exception as e:
        print(f"An error occurred during test: {e}")
    finally:
        conn.close()
        # Clean up the dummy file if it still exists
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

if __name__ == "__main__":
    test_clear_history()
