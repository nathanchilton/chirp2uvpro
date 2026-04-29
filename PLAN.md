# Plan: Backend-Driven Repeater Import and Merging

The goal is to move the repeater import and merging logic from the client-side JavaScript to the Python backend, following HTMX design principles. This will ensure that the "pinning" UI is triggered correctly and that different input formats (CSV vs. Clipboard) are handled robustly without data loss.

## Objectives
- Move merging logic from `main.js` to `routes.py`.
- Support merging new repeaters into both BTECH Clipboard format and CSV formats.
- Prevent accidental overwriting of CSV data when importing repeaters.
- Ensure the pinning UI is triggered only when existing BTECH Clipboard data is present.

## Implementation Steps

### 1. Backend Refactoring (`src/app/api/routes.py`)
- Update the `/api/import-repeaters` endpoint to accept `current_content` (the text currently in the textarea).
- Implement logic to:
    - Parse `current_content` to detect format (BTECH Clipboard vs. CSV).
    - If BTECH Clipboard: Return the new repeaters and a signal to show the pinning UI (`action: "show_pinning"`).
    - If CSV: Append the new repeaters as new rows (in a compatible format) and return the updated CSV content with a signal to update the text only (`action: "update_text"`).
    - If empty: Return new repeaters and a signal to update the text (`action: "update_text"`).
- Ensure the response JSON structure is consistent, e.g.:
  ```json
  {
    "action": "show_pinning" | "update_text",
    "repeaters": [...],
    "updated_content": "..."
  }
  ```

### 2. Frontend Refactoring (`src/app/static/js/main.js`)
- Update `handleImportRepeaters` to:
    - Extract `currentContent` from the textarea.
    - Send `currentContent` to the `/api/import-import-repeaters` endpoint.
    - Handle the new response structure:
        - If `action === "show_pinning"`: Proceed with the existing pinning UI logic (using the `repeaters` array).
        - If `action === "update_text"`: Update the textarea with `updated_content` and show a success alert.

### 3. Verification
- Verify that importing repeaters when the textarea has BTECH Clipboard content triggers the pinning UI.
- Verify that importing repeaters when the textarea has CHIRP/BTECH CSV content appends the new repeaters to the CSV without losing existing data.
- Verify that importing repeaters when the textarea is empty correctly populates it with the new format.
