import pytest
import os
from playwright.sync_api import Page, expect
from tests.e2e.test_conversion_flow import server, BASE_URL

def test_conversion_history_link_works(page: Page):
    """
    Test that clicking a link in the Conversion History leads to a valid download.
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)

    # 2. We need to have something in history first. 
    # Since we don't want to rely on existing state, we'll assume there might be some 
    # if we run it in a persistent environment, but for a clean test, we should 
    # probably do an upload first.
    
    # For this test, let's use the upload method to create a history entry.
    # We'll use a temporary file.
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(b"Location,Name,Frequency\n1,Test,100.0\n")
        tmp_path = tmp.name

    try:
        # 3. Switch to "Upload File" tab
        page.click('#upload-tab')

        # 4. Select the file to upload
        page.set_input_files('#file-input', tmp_path)

        # 5. Click the Upload and Convert button
        page.click('#upload-button')

        # 6. Wait for the result to appear
        result_locator = page.locator("#result")
        expect(result_locator).to_contain_text("uploaded and converted successfully!", timeout=10000)

        # 7. Now check the history section
        # Wait for history to load
        history_list = page.locator("#history-list")
        expect(history_list).to_be_visible()

        # 8. Find the link in history and click it
        # The link should contain the filename or at least be present
        history_link = page.locator("#history-list a").first
        expect(history_link).to_be_visible()
        
        href = history_link.get_attribute("href")
        assert href is not None
        assert href.startswith("/downloads/")

        # 9. Clicking the link should trigger a download
        # In Playwright, we can catch the download event
        with page.expect_download() as download_info:
            history_link.click()
        
        download = download_info.value
        assert download.suggested_filename.startswith("converted_")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
