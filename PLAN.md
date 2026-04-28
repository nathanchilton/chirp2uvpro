# Plan: RepeaterBook Import Feature

## Overview
Implement a feature that allows users to automatically update their channel list with the closest repeaters using a mock RepeaterBook API. The feature will include location detection, a way to "pin" existing channels to prevent them from being overwritten, and a final output in the "clipboard format".

## Objectives
- [x] Implement a mock Repeambook API that returns 30 repeaters based on a given location.
- [x] Integrate browser Geolocation API to detect user location.
- [x] Add a "RepeaterBook Import" button to the UI.
- [x] Implement a channel selection interface to allow "pinning" of existing channels.
- [x] Implement the logic for merging pinned channels with new repeater channels (up/to 30 total).
- [x] Ensure the final output is updated in the "clipboard format".

## Implementation Steps

### 1. Research and Setup
- [x] Analyze existing channel management and "clipboard format" generation logic.
- [x] Identify the best place to integrate the new import logic within the current application flow.

### 2. Mock API Development
- [x] Create a mock function `getMockRepeaters(location)` that:
    - [x] Takes latitude and longitude as input.
    - [x] Returns a list of 30 simulated repeater objects (name, frequency, etc.).
    - [x] Provides a variety of frequencies to simulate real-world scenarios.

### 3. Core Feature Logic
- [x] Implement `detectUserLocation()` using `navigator.geolocation`.
- [x] Implement `handleRepeaterBookImport()`:
    - [x] If "Text Input" is empty:
        - [x] Fetch mock repeaters for current location.
        [x] Update "Output Text" with these 30 channels in clipboard format.
    - [x] If "Text Input" is NOT empty:
        - [x] Parse existing channels from "Text Input".
        - [x] Display a list of these channels with checkboxes.
        - [x] Wait for user to click a "Confirm" button.
    - [x] Upon confirmation:
        - [x] Fetch mock repeaters for current location.
        - [x] Combine "pinned" (checked) channels with new repeaters.
        - [x] Maintain a maximum of 30 channels (prioritizing pinned ones, then filling the rest with new ones).
        - [x] Update "Output Text" with the resulting list in clipboard format.

### 4. UI/UX Implementation
- [x] Add "RepeaterBook Import" button.
- [x] Create the "Pinning Interface" (modal or inline list) with:
    - [x] List of current channels.
    - [x] Checkboxes for each channel.
    - [x] "Confirm" button.
- [x] Ensure the interface is mobile-friendly.

### 5. Testing and Validation
- [x] Unit tests for `getMockRepeaters`.
- [x] Unit tests for the merging logic (handling empty input, handling non-empty input, respecting the 30-channel limit, respecting pinned channels).
- [ ] Manual end-to-end testing using a browser simulator for geolocation.
- [ ] Verify output format matches the "clipboard format" standard.
