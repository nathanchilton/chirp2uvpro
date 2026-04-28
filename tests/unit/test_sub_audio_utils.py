import pandas as pd
from src.converter.utils import format_sub_audio_to_hz, format_sub_audio_to_mhz

def test_sub_audio():
    # Test 1: Input is kHz (e.g., 0.1 kHz -> 100 Hz)
    val_khz = 0.1
    hz = format_sub_audio_to_hz(val_khz)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_khz} kHz -> Hz: {hz}, MHz: {mhz}")
    assert hz == 100
    assert mhz == 0.0001

    # Test 2: Input is kHz (e.g., 0.1318 kHz -> 131.8 Hz)
    val_khz_ctcss = 0.1318
    hz = format_sub_audio_to_hz(val_khz_ctcss)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_khz_ctcss} kHz -> Hz: {hz}, MHz: {mhz}")
    assert hz == 131.8
    assert mhz == 0.0001318

    # Test 3: Input is DCS (e.g., 23)
    val_dcs = 23
    hz = format_sub_audio_to_hz(val_dcs)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_dcs} DCS -> Hz: {hz}, MHz: {mhz}")
    assert hz == 23
    assert mhz == 0.000023

    # Test 4: Input is an invalid value (e.g., "abc")
    val_invalid = "abc"
    hz = format_sub_audio_to_hz(val_invalid)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_invalid} -> Hz: {hz}, MHz: {mhz}")
    assert hz == 0.0
    assert mhz == 0.0

    # Test 5: Input is Hz (e.g., 100 Hz)
    val_hz = 100
    hz = format_sub_audio_to_hz(val_hz)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_hz} Hz -> Hz: {hz}, MHz: {mhz}")
    assert hz == 100
    assert mhz == 0.0001

    print("All tests passed!")

if __name__ == "__main__":
    test_sub_audio()
