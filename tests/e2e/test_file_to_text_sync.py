import pytest
import os
import re
from playwright.sync_api import Page, expect
from tests.e2e.test_conversion_flow import BASE_URL

TEST_FILE_PATH = os.path.abspath("tests/e2e/tmp/test_chirp.csv")
EXPECTED_CONTENT = "Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM"

def test_file_upload_syncs_to_text_area(page: Page):
    """
    Test that uploading a file automatically populates the text input textarea.
    """
    # 1. Navigate to the application
    page.goto(BASE_URL)

    # 2. Switch to "Upload File" tab
    page.click('#upload-tab')

    # 3. Select the file to upload
    page.set_input_files('#file-input', TEST_FILE_PATH)

    # 4. Switch to "Text Input" tab
    page.click('#text-tab')

    # 5. Wait for the textarea to be populated (it might take a moment due to FileReader)
    textarea = page.locator('textarea[name="csv_content"]')
    textarea.wait_for(state="visible")
    
    # Wait for the value to not be empty
    page.wait_for_function('document.querySelector(\'textarea[name="csv_content"]\').value !== ""')

    # 6. Verify the textarea contains the content of the uploaded file
    # Use strip() to avoid issues with trailing newlines in the test file
    expect(textarea).to_have_value(re.compile(re.escape(EXPECTED_CONTENT)))
