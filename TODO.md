# Project TODO List

## Phase 2: Application Framework Setup
- [x] Set up project structure (templates, static directory, and static file configuration)
- [ ] Implement basic frontend scaffolding with HTMS and a CSS framework
- [ ] Define API endpoints for file upload, conversion, and history retrieval

## Phase 3: Persistence and File I/O
- [ ] Design and implement the SQLite schema (history, file metadata)
- [ ] Implement backend logic for managing uploaded and converted files
- [ ] Implement the backend endpoint for processing copy/pasted CSV content

## Phase 4: Feature Implementation
- [ ] Implement 30-channel truncation logic with user-facing warnings
- [ ] Develop the HTMX-driven UI for file selection, conversion triggering, and results display
- [ ] Implement the bi-directional conversion routes on the backend
- [ ] Implement the "Conversion History" view
- [ ] Implement the "Delete History" functionality
- [ ] Implement robust error handling for malformed CSV data (ensuring `ConversionError` is caught and displayed)

## Phase 5: Testing and Refinement
- [ ] Implement Playwright end-to-end tests for the full user flow (upload $\to$ convert $\to$ download)
- [ ] Perform a final code cleanup and performance optimization
