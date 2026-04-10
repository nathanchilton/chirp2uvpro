import pytest
import os
from playwright.sync_api import Page, expect
from tests.e2e.test_conversion_flow import server, BASE_URL

TEST_FILE_PATH = os.path.abspath("tests/e2e/tmp/test_chirp.csv")

def test_conversion_flow_upload_chirps_to_btech(page: Page):
    """
    Test the full conversion flow using the upload method (CHIRP -> BTECH).
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)

    # 2. Switch to "Upload File" tab
    # In converter_ui.html, the "Upload File" tab has hx-get="/converter-file-ui"
    page.click('button:has-text("Upload File")')

    # 3. Ensure we are in the file upload UI
    expect(page.locator(".converter-file-ui")).to_be_visible()
    expect(page.locator("h3.converter-title")).to_contain_text("Upload and Convert CSV")

    # 4. Select the file to upload
    page.set_input_files('input[type="file"]', TEST_FILE_PATH)

    # 5. Click the Upload and Convert button
    page.click('button:has-text("Upload and Convert")')

    # 6. Wait for the result to appear and verify success
    # The target is #upload-result
    result_locator = page.locator("#upload-result")
    expect(result_locator).to_contain_text("uploaded and converted successfully!", timeout=10000)

    # 7. Check if the success alert is present
    # The backend returns an alert fragment, which might be inside #upload-result or appended.
    # Based on the previous test, it checks for .alert-success
    expect(page.locator(".alert-success")).to_be_visible()

    # 8. Verify the download link is present and has a correct filename
    # The backend returns: <a href="{download_url}" class="btn btn-sm btn-success" download>Download Converted File</a>
    # Wait for the link to appear as it's part of the HTMX swap
    download_link = page.locator('a:has-text("Download Converted File")')
    expect(download_link).to_be_visible()
    
    # The download attribute is not explicitly set to the filename in the upload route, 
    # it just uses the default browser behavior or the href.
    # But let's check if the href contains 'converted_'
    href = download_link.get_attribute("href")
    assert href is not None
    assert "converted_" in href

