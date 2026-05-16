# Test Audit and Correction Design

## Problem Statement

Tests in the `chirp2uvpro` project make assumptions about the BTECH, CHIRP, and Clipboard
format structures that are inconsistent with the actual reference files produced by the
BTECH and CHIRP applications. Some reference files were previously edited to match test
expectations, which was incorrect. The reference files (`tests/data/example_*`) are the
ground truth and must never be modified. Tests must be corrected to match the reference
files, and then the parser/generator code can be fixed to pass the corrected tests.

## Clipboard Sub-Audio Encoding Convention

The clipboard format uses a single field (`ts` / `rs`) for both CTCSS tones and DCS codes:

- **CTCSS frequencies** are stored as the frequency multiplied by 100.
  - Example: `13180` represents 131.8 Hz (131.8 × 100 = 13180)
  - Example: `10000` represents 100.0 Hz (100.0 × 100 = 10000)
- **DCS codes** are stored as the raw code value (< 1000).
  - Example: `47` represents DCS code 047
  - Example: `23` represents DCS code 023

**Heuristic**: if the value > 1000, treat it as CTCSS (divide by 100 to get Hz). If ≤ 1000, treat it as DCS code.

This impacts parsing logic (the threshold was previously 2000, which may be incorrect) and all clipboard-related tests.

## Reference Files (Ground Truth - DO NOT MODIFY)

| File | Format | Key Characteristics |
|---|---|---|
| `tests/data/example_btech_format.csv` | Native BTECH CSV | Columns: `title,tx_freq,rx_freq,tx_sub_audio(...),rx_sub_audio(...),tx_power(...),bandwidth(...),scan(...),talk around(...),pre_de_emph_bypass(...),sign(...),tx_dis(...),bclo(...),mute(...),rx_modulation(...),tx_modulation(...)` — NO `duplex`, `offset`, `location`, `skip` columns. Frequencies in Hz. Sub-audio in Hz (e.g., `13180` = 131.8 Hz). |
| `tests/data/example_chirp_format.csv` | CHIRP CSV | Columns: `Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE`. Frequencies in MHz. Sub-audio in Hz. |
| `tests/data/example_clipboard_format.txt` | Clipboard JSON | Format: `Copy this text and start BTECH UV` + JSON with `chs` array. JSON keys: `n`, `rf`, `tf`, `ts`, `rs`, `s`, `id`, `p`. Frequencies in MHz. Sub-audio in 0.01Hz units (e.g., `13180` = 131.8 Hz). |

## Known Issues Identified

### Test Assertions That Don't Match Reference Files

1. **`test_comprehensive_roundtrip.py`** — Uses `example_comprehensive_btech.csv` as input, which is NOT a ground truth reference file. It has a different column set/order than `example_btech_format.csv`. Must decide: either fix this test to use the real reference file, or update assertions to match what the comprehensive file actually contains.

2. **`test_flag_roundtrip.py`** — Prepends `"BTECH UV\n"` to `example_btech_format.csv` content and parses it. This assumes the reference file needs a prefix to parse correctly. Need to verify whether the parser handles the ref file without this prefix.

3. **`test_roundtrip.py`** — Uses `ChirpParser` to parse BTECH content, which is semantically incorrect (though functionally may work because ChirpParser detects `tx_freq` column and uses Hz scale). Should test proper BTECH→CHIRP→BTECH pipeline.

4. **`test_api.py::test_api_paste_form_encoded_btech_to_chirp`** — Contains typo `14_6520000` instead of `146520000` in the BTECH content. This causes the test to fail because the parser can't parse the frequency.

5. **`test_btech_duplex_inference.py`** — Uses a BTECH CSV header that includes `duplex,offset,location,skip` columns, which don't exist in the reference BTECH format. The test content may need adjustment.

6. **`test_btech_sub_audio_sync.py`** — Uses a bare CSV without a `BTECH UV` prefix. The header is `title,tx_freq,rx_freq,tx_sub_audio,rx_sub_audio`. This may parse correctly (BtechParser detects `title` in columns and treats Hz scale when no prefix). Need to verify.

7. **`test_btech_sub_audio_logic.py`** — Uses CSV header `title,tx_freq,rx_freq,duplex,offset,tx_sub_audio,...` — includes `duplex,offset` columns not in reference. Also has `pre_de_emphasis_bypass` (note: emphasis not emph) which may not match the parser's column lookup.

8. **`test_btech_parser_fix.py`** — Tests with various BTECH-like formats. The CSV prefix tests may need checking against reference format.

9. **`test_chirp_roundtrip_regression.py`** — Roundtrips CHIRP→BTECH→CHIRP using the example files. Side-effect: writes intermediate files to `tests/data/output_btech.csv` and `tests/data/output_chirp_back.csv`, which should be in temp dirs.

10. **`test_clipboard_pretty_json.py`** — Asserts `tx_sub_audio_hz == 13180.0` after parsing `"ts": 1318000`. Need to verify parsing logic: 1318000 (0.01Hz units) → 13180.0 Hz? Or is it 13180.0 Hz? The reference file uses `ts: 13180` → 131.8 Hz.

11. **`test_import_flow.py`** — Python syntax error: `await` used outside async function at line 43.

### Parser/Generator Issues

1. **`BtechGenerator`** outputs columns `duplex,offset,location,skip` that don't exist in the reference BTECH format.
2. **`BtechParser`** reads `duplex,offset,location,skip` columns but also handles their absence. Column matching uses `find_col()` with keywords which may have edge cases.
3. **`ChirpGenerator`** column `cToneF` vs reference `cToneFreq` — mismatch between generator output header and CHIRP reference file header name.

## Approach

### Phase 1: Audit All Tests
Create one beads task to systematically audit every test file and document each assertion mismatch against the reference files.

### Phase 2: Fix Tests in Groups (parallelizable)
Create one beads task per test group, each dependent on the audit task:

| Task | Test Files | Description |
|---|---|---|
| T2a | `test_roundtrip.py`, `test_comprehensive_roundtrip.py`, `test_flag_roundtrip.py` | Fix BTECH roundtrip tests to use correct reference format expectations |
| T2b | `test_btech_duplex_inference.py`, `test_btech_sub_audio_sync.py`, `test_btech_sub_audio_logic.py`, `test_btech_sub_audio_no_mirroring.py`, `test_btech_sub_audio_bug.py` | Fix BTECH sub-audio and duplex tests |
| T2c | `test_btech_parser_fix.py`, `unit/test_converter.py`, `unit/test_logic_csv.py`, `unit/test_logic_fix.py` | Fix BTECH parser unit tests |
| T2d | `test_chirp_roundtrip_regression.py`, `test_chirp_generator.py` | Fix CHIRP roundtrip/generator tests |
| T2e | `test_clipboard_roundtrip.py`, `test_clipboard_identification_regression.py`, `test_clipboard_pretty_json.py`, `test_mock_api_to_clipboard.py` | Fix clipboard format tests |
| T2f | `tests/integration/test_api.py` | Fix integration API tests (typo, expectations) |
| T2g | `tests/e2e/test_import_flow.py` | Fix syntax error in import E2E test |
| T2h | `tests/e2e/test_conversion_flow.py` | Fix E2E conversion flow tests if needed |
| T2i | `tests/unit/test_logic_refactor.py` | Fix refactor logic tests if needed |

### Phase 3: Fix Parser/Generator Code
Create one beads task dependent on all T2 tasks. After all tests are corrected (and presumably failing because the code doesn't match the reference format), fix `btech.py`, `chirp.py`, `clipboard.py` parsers and generators to match the reference files.

### Phase 4: Final Verification
Run all tests, verify everything passes, and commit.

## Dependency Graph

```
Phase 1: [T1: Audit tests]
               |
     ┌─────┬───┼───┬─────┬─────┬─────┬─────┐
     T2a  T2b T2c T2d  T2e  T2f  T2g  T2h  T2i
               |
          [T3: Fix parser/generator code]
               |
          [T4: Final verification & commit]
```

## Success Criteria

1. All tests pass with zero failures
2. No modifications to any `tests/data/example_*` file
3. Each test correctly represents what the reference format actually contains
4. Parser/generator code correctly handles the format as defined by the reference files
