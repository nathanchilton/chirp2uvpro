# TODO List

## Current Task: Review Tests against Reference Files
- [x] Explore the codebase to identify relevant tests for CHIRP, BWE/BTECH UV-PRO, and Clipboard Sharing formats
- [x] Examine reference files for format specifications:
    - Yaesu_VX-6_20240203-Jacksonville.csv (CHIRP)
    - ham_and_gmrs.csv (BTECH UV-PRO)
    - clipboard_sharing_format.txt (Clipboard $\text{Sharing}$)
- [x] Review CHIRP format tests against Yaesu_VX-6_20240203-Jacksonville.csv
- [x] Review BTECH UV-PRO format tests against ham_and_gmrs.csv
- [x] Review Clipboard Sharing format tests against clipboard_sharing_format.txt
- [x] Fix any identified inconsistencies in the tests
- [x] Run all tests using pytest to verify fixes and ensure no regressions


## Previous Tasks (Refactoring Plan: Parser/Generator Pattern)
## 1. Complete implementation of BtechParser in src/converter/btech.py
- [x] Fix `ChipGenerator` -> `ChirpGenerator` typo
- [x] Implement frequency and duplex logic
- [x] Implement sub-audio and mode logic
- [x] Implement bandwidth and power logic

## 2. Refactor src/converter/logic.py wrappers
- [x] Update `clipboard_to_btech` (or similar) to use `ClipboardParser` and `BtechGenerator`
- [x] Update `chirp_to_btech` to use `ChirpParser` and `BtechGenerator`
- [x] Update `btech_to_chirp` to use `BtechParser` and `ChirpGenerator`
- [x] Update `internal_to_clipboard` to use `ClipboardGenerator`

## 3. Verification and Testing
- [x] Run reproduction script `repro_prefix_failure.py`
- [x] Run existing test suite
- [x] Add new tests for refactored wrappers
