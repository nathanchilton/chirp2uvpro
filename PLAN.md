# Plan for Universal Radio Frequency Channel Format Implementation

## Overview
The goal is to establish a robust, "universal" internal format for radio frequency channel data that can accurately represent information from various source formats (BTECH, CHINT, Clipboard). This involves analyzing existing reference files, documenting all formats, defining the new universal format, updating/writing tests, fixing existing conversion bugs, and finally refactoring the codebase for better maintainability.

## Phase 1: Analysis and Discovery
**Objective:** Understand the nuances, differences, and overlaps between the existing reference formats.

1.1 **Examine Reference Files**
- Read `tests/data/example_btech_format.csv`.
- Read `tests/data/example_chirp_format.csv`.
- Read `tests/data/example_clipboard_format.txt`.
- Identify common channels (e.g., "N5RCA", "2MCALL") to use as anchors for comparison.
- Note differences in:
    - Field names.
    - Data types (string, number, etc.).
    - Units and precision (e.g., Hz vs. MHz).
    - Presence/absence of specific fields (e.g., CTCSS, Offset, Power).

## Phase 2: Documentation and Specification
**Objective:** Create a "source of truth" for all formats to guide implementation and testing.

2.1 **Format Documentation**
- Create a document detailing the structure of the BTECH format.
- Create a document detailing the structure of the CHIRP format.
- Create a document detailing the structure of the Clipboard format.
- Each document must specify: Field Name, Data Type, and Precision/Units.

2.2 **Internal Format Specification**
- Define the "Universal/Internal" format.
- Document all fields required to represent the union of all information found in Phase 1.
- Ensure the format is flexible enough to handle missing data from certain source formats (e.g., using optional fields or nulls).

## Phase 3: Test Infrastructure Development
**Objective:** Establish a testing baseline that matches the reference files and validates all conversion directions.

3.1 **Update Existing Tests**
- Review current tests and update them to ensure they reflect the content and structure of the reference files.
- Ensure tests do not attempt to modify the reference files themselves.

3/2 **Implement New Conversion Tests**
- Write tests for:
    - `BTECH -> Internal`
    - `CHIRP -> Internal`
    - `Clipboard -> Internal`
    - `Internal -> BTECH`
    - `Internal -> CHIRP`
    - `Internal -> Clipboard`
- Use the identified common channels to verify data integrity across transformations (e.g., verifying that frequency remains correct even if the unit changes from Hz to MHz).

## Phase 4: Implementation and Bug Fixing
**Objective:** Correct the existing conversion logic to align with the new specifications.

4.1 **Identify and Fix Bugs**
- Run the new test suite.
- Identify failures where the current code produces incorrect output or fails to handle format-specific nuances.
- Fix the code to ensure all conversion tests (from Phase 3.2) pass.

## Phase 5: Refactoring and Optimization
**Objective:** Improve code quality and maintainability now that a solid test suite is in place.

5.1 **Code Refactoring**
- Refactor the conversion logic to use the newly defined "Universal Format" as the primary engine.
- Clean up the codebase, improving modularity and readability.
- Ensure all tests (existing and new) pass after refactoring to prevent regressions.
