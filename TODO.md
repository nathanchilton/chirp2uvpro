# Project TODO List

## Current Sprint: Conversion Flow Completion

- [x] Repair corrupted HTML/Jinja in src/app/templates/partials/converter_ui.html
- [x] Investigate and fix 400 Bad Request in /api/convert/paste endpoint
    - [x] 1.1 Check request payload in E2E test
    - [x] 1.2 Verify direction parameter handling in routes.py
    - [x] 1.3 Verify csv_content extraction from JSON/Form
- [x] Implement empty state for Conversion History section
    - [x] 1.1 Locate history fragment template
    - [x] 1.2 Implement empty state logic in template
    - [ ] 1.3 Verify history is displayed when conversions exist
    - [ ] 1.4 Verify empty state is displayed when no conversions exist
- [x] Run E2E tests to verify all conversion flows
- [ ] Create integration test for history display
    - [ ] 2.1 Implement test case for existing history
    - [ ] 2.2 Implement test case for empty history

## Phase 2: Application Framework Setup

- [x] Set up project structure (templates, static directory, and static file configuration)
- [x] Implement basic frontend scaffolding with HTMS and a SS framework
- [x] Define API endpoints for file upload, conversion, and history retrieval

## Phase 3: Persistence and File I/O

- [x] Design and implement the SQLite schema (history, file metadata)
- [x] Implement backend logic for managing uploaded and converted files
- [x] Implement the backend endpoint for processing copy/pasted CSV content

## Phase 4: Feature Implementation

- [x] Implement 30-channel truncation logic with user-facing warnings
- [x] Develop the HTMX-driven UI for file selection, conversion triggering, and results display
- [x] Implement the bi-directional conversion routes on the backend
- [x] Implement the "Conversion History" view
- [x] Implement Playwright end-to-end tests for the full user flow (paste $\to$ conversion $\to$ download)
- [x] Implement E2E tests for File Upload and Download functionality
    - [x] 4.1 Create new E2E test case for file upload flow
    - [x] 4.2 Simulate file upload using Playwright `set_input_files`
    - [x] 4.3 Assert success alert and download link presence/attributes
- [ ] Implement integration tests for database persistence (conversion history)
- [ ] Expand unit testing for core conversion logic
- [ ] Perform a final code cleanup and performance optimization
