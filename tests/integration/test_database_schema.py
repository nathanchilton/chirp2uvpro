import sqlite3
import os
import sys

# Ensure the src directory is in the python path so we can import the database module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from database import init_db, get_db_connection

def test_db_tables_exist():
    """
    Verify that the database initialization creates the required tables.
    This test checks the existence of 'conversion_history' and 'uploaded_files'.
    """
    # Initialize the database (this should create the tables if they don't exist)
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check for conversion_history table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversion_history';")
        history_table = cursor.fetchone()
        assert history_table is not None, "Table 'conversion_history' was not found."
        
        # Check for uploaded_files table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='uploaded_files';")
        uploaded_files_table = cursor.fetchone()
        assert uploaded_files_table is not None, "Table 'uploaded_files' was not found."
        
    finally:
        conn.close()
