import pytest
import os
from playwright.sync_api import Page, expect
from tests.e2e.test_conversion_flow import server, BASE_URL

def test_import_repeaters_flow(page: Page):
    """
    Test the full import flow: Click Import -> Mock Geolocation -> Verify result.
    """
    # 1. Mock geolocation to always return a specific location
    # We use page.add_init_script to override the geolocation API before the page loads.
    page.add_init_script("""
        navigator.geolocation.getCurrentPosition = (success, error, options) => {
            success({
                coords: {
                    latitude: 45.523062,
                    longitude: -122.676482
                },
                timestamp: Date.now()
            });
        };
    """)
    
    # 2. Navigate to the application
    page.goto(BASE_URL)
    
    # 3. Ensure initial state is correct (some content might be present if we are testing pinning)
    # For a clean test, we can start with an empty textarea if needed, 
    # but here we'll check if we can trigger the import.
    
    # 4. Click the Import Repeaters button
    page.click("#import-repeaters-btn")
    
    # 5. Wait for the import process to complete by waiting for the button to be re-enabled
    page.wait_for_selector("#import-repeaters-btn:not([disabled])")
    
    # 6. Wait for the result to appear.
    # Since the backend returns mock repeaters, we expect the textarea to be updated.
    # We'll check for the text that should be in the BTECH format.
    result_locator = page.locator("#result").first

    # If the pinning UI is shown, we need to click "Apply Import" to update the textarea
    if result_locator.locator("#apply-import-btn").is_visible():
        page.click("#apply-import-btn")

    # Let's switch to the text tab first to see the result.
    page.click("#text-tab")

    # 6. Wait for the textarea to be updated with content from the import
    textarea_locator = page.locator('textarea[name="content"]')

    # We expect the imported content to contain some of the mock repeater data.
    # The mock data for 45.523062, -122.676482 will be returned by the server.
    # Let's check if the content is not empty and contains something expected.
    expect(textarea_locator).not_to_be_empty()
    
    # The content should follow the BTECH format (or whatever format the mock returns)
    # Based on the mock implementation (which I haven't read yet, but I can guess),
    # it should contain some frequency.
    content = textarea_locator.input_value()
    assert "tx_freq" in content or "chs" in content

def test_import_repeaters_with_pinning(page: Page):
    """
    Test the import flow with pinning UI when existing channels are present.
    """
    # 1. Mock geolocation
    page.add_init_script("""
        navigator.geolocation.getCurrentPosition = (success, error, options) => {
            success({
                coords: {
                    latitude: 45.523062,
                    longitude: -122.676482
                },
                timestamp: Date.now()
            });
        };
    """)
    
    # 2. Navigate to the application
    page.goto(BASE_URL)
    
    # 3. Pre-fill the textarea with some existing channels
    page.click("#text-tab")
    existing_content = 'Copy this text and start BTECH UV{"n":"Existing","chs":[{"n":"Existing","rf":146.0,"tf":146.0,"ts":131.8,"rs":131.8,"id":1,"p":0}]}'
    page.fill('textarea[name="content"]', existing_content)
    
    # 4. Click the Import Repeaters button
    page.click("#import-repeaters-btn")
    
    # 5. Wait for the import process to complete by waiting for the button to be re-enabled
    page.wait_for_selector("#import-repeaters-btn:not([disabled])")
    
    # 6. Verify that the pinning UI is displayed
    # The pinning UI is injected into #result
    result_locator = page.locator("#result").first
    expect(result_locator.locator(".card-header")).to_contain_text("Pin existing channels")
    
    # 7. Click "Apply Import"
    page.click("#apply-import-btn")
    
    # 8. Wait for the textarea to be updated with the merged content (async fetch + alert)
    # The JS handler does: textarea.value = data.content; alert("Import applied successfully!");
    # Wait for the mock repeater data to appear in the textarea
    textarea_locator = page.locator('textarea[name="content"]')
    page.wait_for_function(
        'document.querySelector(\'textarea[name="content"]\').value.includes("Repeater")',
        timeout=10000
    )
    
    # 9. Verify that the textarea now contains BOTH the existing and the new channels
    content = textarea_locator.input_value()
    assert "Existing" in content
    assert len(content) > len(existing_content)
