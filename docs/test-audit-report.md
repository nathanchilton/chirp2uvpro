# Test Audit Report

Generated: 2026-05-16
Task: T1 - Audit all test assertions against reference files

## Reference Files Summary

| File | Type | Key Traits |
|---|---|---|
| `example_btech_format.csv` | Native BTECH CSV | No `BTECH UV` prefix. Columns: `title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),...,talk around(...),pre_de_emph_bypass(...),...,tx_modulation(...)`. NO `duplex`, `offset`, `location`, `skip`. `talk around` has a space. Freq in Hz. Sub-audio appears to be in 0.01Hz units (13180=131.8Hz). |
| `example_chirp_format.csv` | CHIRP CSV | `Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,...`. Freq in MHz. Sub-audio in Hz. |
| `example_clipboard_format.txt` | Clipboard JSON | `Copy this text and start BTECH UV{chs:[...]}`. Keys: n, rf, tf, ts, rs, s, id, p. Freq in MHz. Sub-audio: >1000 = CTCSS*100, ≤1000 = DCS code. |
| `example_comprehensive_btech.csv` | Hand-crafted test data | Not a native BTECH export. Has typos (`CTCSS=fmt/`, `0=MS/1=ON`). Includes `location,skip,offset,duplex` columns not in native format. |

---

## Test-by-Test Audit

### 1. `tests/test_roundtrip.py`
- **Uses:** `example_btech_format.csv`
- **Method:** `ChirpParser` → `ChirpGenerator` → `BtechParser`
- **Checks:** tx_freq, rx_freq, name only
- **Issues:**
  - Uses ChirpParser to read BTECH data (semantically wrong but may function)
  - Only checks 3 fields; should verify more fields

### 2. `tests/test_comprehensive_roundtrip.py`
- **Uses:** `example_comprehensive_btech.csv`
- **Method:** `BtechParser` → `ChirpGenerator` → `ChirpParser` → `BtechGenerator`
- **Checks:** name, tx_freq, rx_freq, tx_sub_audio, rx_sub_audio, tx_power, scan, talk_around, mute, sign, tx_dis, bclo, pre_de_emph_bypass
- **Issues:**
  - Input file is NOT a native BTECH export (has typos, extra columns)
  - Input CSV starts with `BTECH UV\n` prefix (may affect parsing scale)

### 3. `tests/test_flag_roundtrip.py`
- **Uses:** `example_btech_format.csv` (with `"BTECH UV\n"` prepended)
- **Method:** `BtechParser` → `ChirpGenerator` → `ChirpParser` → `BtechGenerator`
- **Checks:** scan, talk_around, mute, sign, tx_dis, bclo on first channel
- **Issues:**
  - Artificially prepends prefix not in the original reference file

### 4. `tests/test_btech_duplex_inference.py`
- **Uses:** Inline CSV with `duplex,offset,location,skip` columns
- **Issues:**
  - CSV has columns not in reference BTECH format
  - Column `b_clo` instead of `bclo` — won't match parser

### 5. `tests/test_btech_sub_audio_sync.py`
- **Uses:** Inline CSV header `title,tx_freq,rx_freq,tx_sub_audio,rx_sub_audio`
- **Expects:** tx_sub_audio_hz == 1000.0 for value `1000`
- **Issues:**
  - If BTECH CSV sub-audio is in 0.01Hz units, then `1000` * 0.01 = 10 Hz, not 1000 Hz
  - Parser currently treats as Hz (format_sub_audio_to_hz(1000, 'Hz') = 1000.0)

### 6. `tests/test_btech_sub_audio_logic.py`
- **Uses:** Inline CSV with `BTECH UV\n` prefix, frequencies as `462.0`, sub-audio as `13180`
- **Expects:** CTCSS test: tx_sub_audio_hz == 131.8 for value `13180`
- **Issues:**
  - CSV has `duplex,offset,location,skip` columns (not in reference)
  - Column name `pre_de_emphasis_bypass` (wrong spelling — parser looks for `pre_de_emph_bypass`)
  - If scale='Hz' (from BTECH UV prefix), format_sub_audio_to_hz(13180, 'Hz') = 13180, not 131.8
  - Frequencies `462.0` with scale='Hz' = 462 Hz, not 462 MHz — test doesn't check freq so passes

### 7. `tests/test_btech_sub_audio_no_mirroring.py`
- **Uses:** JSON content through BtechParser._parse_channel_append
- **Expects:** tx_sub_audio_hz == 100000, rx_sub_audio_hz == 200000
- **Issues:**
  - _parse_channel_append uses format_sub_audio_to_hz(val, scale='Hz')
  - 100000 * 1 = 100000 Hz — not a valid CTCSS tone. If 0.01Hz: 1000 Hz.

### 8. `tests/test_btech_sub_audio_bug.py`
- **test_ctcss_sub_audio_regression:** Generator→Parser roundtrip with 1000.0 Hz
- **test_btech_uv_sub_audio_regression:** Creates CSV with `BTECH UV` prefix, value `100000`, expects `1000.0`
- **Issues:**
  - Roundtrip test is self-consistent (both gen and parser may be wrong same way)
  - BTECH UV prefix test: expects 100000 → 1000.0, but parser with scale='Hz' gives 100000.0
    = This test SHOULD fail with current parser code

### 9. `tests/unit/test_btech_parser_fix.py`
- **Tests:** Various JSON and CSV BTECH formats with prefix/no-prefix
- **Issues:**
  - Has duplicate function names: `test_btech_parser_with_csv_prefix` defined twice (lines 12 and 38)
  - Has duplicate function names: `test_btech_parser_with_json_no_prefix` defined twice (lines 21 and 46)
  - Has duplicate: `test_btech_parser_with_csv_no_prefix` (lines 29 and 54)
  - Test `test_btech_parser_with_json_prefix` uses `BWE/BTECH JSON` prefix with 'ts' as string '13180'
  - _parse_channel_append uses format_sub_audio_to_hz('13180', 'Hz') = 13180.0, but test doesn't check sub-audio

### 10. `tests/unit/test_converter.py`
- **Tests:** `btech_to_chirp` and `chirp_to_btech` conversion functions
- **Issues:**
  - `test_btech_to_chirp_dcs_ctcss` uses `BTECH_HEADER` constant which has the correct header format
  - Test provides incomplete CSV row: only 16 values for 17 columns (missing last column value)
  - Row: `TestCTCSS,146000000,146500000,100,0,H,25000,0,0,0,1,0,0,0,0` — 16 values, header has 17 columns
  - But wait, our reference file has 17 columns. So this test would get parsing errors or NaN values.

### 11. `tests/unit/test_logic_csv.py`
- **Uses:** Script-based test (no pytest framework)
- **Issues:**
  - Has a comment about a typo `14_6520000` that was fixed

### 12. `tests/integration/test_api.py`
- **`test_api_paste_form_encoded_btech_to_chirp`:** Has typo `14_6520000` in frequency
- Other BTECH tests appear to use minimal headers and may not match reference format

### 13. `tests/e2e/test_import_flow.py`
- **Issues:**
  - Python syntax error: `await` outside async function at line 43
  - Lines 44-45 also use `await` incorrectly

### 14. `tests/test_chirp_roundtrip_regression.py`
- **Issues:**
  - Writes intermediate files to `tests/data/` (should use temp dirs)
  - Generates BTECH from CHIRP example, then CHIRP back from BTECH
  - Checks Name and Frequency match for first 30 channels

### 15. `tests/test_chirp_generator.py`
- **Tests:** ChirpGenerator flag output
- **Issues:**
  - Uses `tx_sub_audio_hz=100000` which is not a valid CTCSS tone (100 kHz)
  - Probably meant 100.0 Hz but stored as 100000 in 0.01Hz units?

### 16. `tests/test_clipboard_roundtrip.py`
- **Uses:** `example_clipboard_format.txt`
- **Expects:** tx_sub_audio_hz == 131.8 for ts:13180
- **Clipboard format:** ts:13180 in 0.01Hz units = 13180 * 0.01 = 131.8 Hz ✓

### 17. `tests/test_clipboard_pretty_json.py`
- **Uses:** Inline JSON with `"ts": 1318000`
- **Expects:** tx_sub_audio_hz == 13180.0
- **Issues:**
  - 1318000 * 0.01 = 13180.0 Hz — not a valid CTCSS tone
  - This test data seems wrong (13180.0 Hz is not a real CTCSS frequency)
  - If this followed the CTCSS convention: 1318000 / 100 = 13180 Hz — still wrong

### 18. `tests/test_clipboard_identification_regression.py`
- **Tests:** ClipboardParser rejects random JSON
- **Issues:**
  - Current parser accepts `{"random": "data"}` because it finds `{` and tries JSON parse
  - The test asserts `len(channels) == 0` but this may fail with current code

### 19. `tests/test_mock_api_to_clipboard.py`
- **Uses:** Mock repeaters through ClipboardGenerator
- **Issues:** None immediately apparent

### 20. `tests/unit/test_logic_refactor.py`
- **Tests:** `internal_to_clipboard` function
- **Issues:** None immediately apparent

---

## CRITICAL FINDING: Sub-audio Scale in BTECH CSV

The native BTECH CSV file (`example_btech_format.csv`) contains sub-audio values like:
- `13180` — should be 131.8 Hz (CTCSS 131.8)
- `13650` — should be 136.5 Hz
- `10000` — should be 100.0 Hz
- `47` — should be DCS code 047
- `16220` — should be 162.2 Hz

These match the **clipboard sub-audio convention** (>1000 = value × 0.01 = Hz, ≤1000 = DCS code).
But the `BtechParser` CSV path uses `format_sub_audio_to_hz(val, scale='Hz')` which treats the
raw value as Hz. This would give 13180 Hz instead of 131.8 Hz — which is wrong.

**This means the BtechParser CSV path has a bug in sub-audio parsing.** It should use
the same 0.01Hz convention as the clipboard format for native BTECH CSV.

---

## Summary of Required Fixes

| Task | File(s) | Primary Issue |
|---|---|---|
| T2a | test_roundtrip.py, test_comprehensive_roundtrip.py, test_flag_roundtrip.py | Roundtrip pipeline and reference file usage |
| T2b | test_btech_duplex_inference.py, test_btech_sub_audio_sync.py, test_btech_sub_audio_logic.py, test_btech_sub_audio_no_mirroring.py, test_btech_sub_audio_bug.py | Duplex/offset/location/skip columns in test content; sub-audio scale |
| T2c | test_btech_parser_fix.py, unit/test_converter.py, unit/test_logic_csv.py, unit/test_logic_fix.py | Duplicate test functions; incomplete CSV rows; wrong scale |
| T2d | test_chirp_roundtrip_regression.py, test_chirp_generator.py | Temp file usage; sub-audio test values |
| T2e | test_clipboard_roundtrip.py, test_clipboard_identification_regression.py, test_clipboard_pretty_json.py, test_mock_api_to_clipboard.py | Sub-audio threshold; test data validity |
| T2f | tests/integration/test_api.py | Typo in frequency value |
| T2g | tests/e2e/test_import_flow.py | Python syntax error (await) |
