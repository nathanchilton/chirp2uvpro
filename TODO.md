# Refactoring Plan: Parser/Generator Pattern

## 1. Complete implementation of BtechParser in src/converter/btech.py
- [x] Fix `ChipGenerator` -> `ChirpGenerator` typo
- [x] Implement frequency and duplex logic
- [x] Implement sub-audio and mode logic
- [x] Implement bandwidth and power logic

## 2. Refactor src/converter/logic.py wrappers
- [ ] Update `clipboard_to_btech` (or similar) to use `ClipboardParser` and `BtechGenerator`
- [ ] Update `chirp_to_btech` to use `ChirpParser` and `BtechGenerator`
- [ ] Update `btech_to_chirp` to use `BtechParser` and `ChirpGenerator`
- [ ] Update `internal_to_clipboard` to use `ChirpGenerator`

## 3. Verification and Testing
- [ ] Run reproduction script `repro_prefix_failure.py`
- [ ] Run existing test suite
