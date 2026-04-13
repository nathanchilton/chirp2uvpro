import pytest
import sqlite3
from playwright.sync_api import Page, expect
from tests.integration.config import BASE_URL

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
        ("test_orig.csv", "test_con.csv", "success", None)
    )
    conn.commit()
    conn.close()

    # 2. Navigate to the application
    page.goto(BASE_URL)

    # 3. Verify the history item is displayed
    history_item = page.locator(".history-list .list-group-item")
    expect(history_item).to_be_visible()
    expect(history_item).to_contain_text("test_orig.csv")
    expect(history_item).to_contain_text("test_con.csv")
    expect(history_item).to_contain_text("success")
