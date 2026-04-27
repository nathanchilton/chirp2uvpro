# Plan: RepeaterBook Import Feature

## Overview
Implement a feature that allows users to automatically update their channel list with the closest repeaters using a mock RepeaterBook API. The feature will include location detection, a way to "pin" existing channels to prevent them from being overwritten, and a final output in the "clipboard format".

## Objectives
- Implement a mock Repeambook API that returns 30 repeaters based on a given location.
- Integrate browser Geolocation API to detect user location.
- Add a "RepeaterBook Import" button to the UI.
- Implement a channel selection interface to allow "pinning" of existing channels.
- Implement the logic for merging pinned channels with new repeater channels (up to 30 total).
- Ensure the final output is updated in the "clipboard format".

## Implementation Steps

### 1. Research and Setup
- [ ] Analyze existing channel management and "clipboard format" generation logic.
- [ ] Identify the best place to integrate the new import logic within the current application flow.

### 2. Mock API Development
- [ ] Create a mock function `getMockRepeaters(location)` that:
    - Takes latitude and longitude as input.
    - Returns a list of 30 simulated repeater objects (name, frequency, etc.).
    - Provides a variety of frequencies to simulate real-world scenarios.

### 3. Core Feature Logic
- [ ] Implement `detectUserLocation()` using `navigator.geolocation`.
- [ ] Implement `handleRepeaterBookImport()`:
    - If "Text Input" is empty:
        - Fetch mock repeaters for current location.
        - Update "Output Text" with these 30 channels in clipboard format.
    - If "Text Input" is NOT empty:
        - Parse existing channels from "Text Input".
        - Display a list of these channels with checkboxes.
        - Wait for user to click a "Confirm" button.
    - Upon confirmation:
        - Fetch mock repeaters for current location.
        - Combine "pinned" (checked) channels with new repeaters.
        - Maintain a maximum of 30 channels (prioritizing pinned ones, then filling the rest with new ones).
        - Update "Output Text" with the resulting list in clipboard format.

### 4. UI/UX Implementation
- [ ] Add "RepeaterBook Import" button.
- [ ] Create the "Pinning Interface" (modal or inline list) with:
    - List of current channels.
    - Checkboxes for each channel.
    - "Confirm" button.
- [ ] Ensure the interface is mobile-friendly.

### 5. Testing and Validation
- [ ] Unit tests for `getMockRepeaters`.
- [ ] Unit tests for the merging logic (handling empty input, handling non-empty input, respecting the 30-channel limit, respecting pinned channels).
- [ ] Manual end-to-end testing using a browser simulator for geolocation.
- [ ] Verify output format matches the "clipboard format" standard.
