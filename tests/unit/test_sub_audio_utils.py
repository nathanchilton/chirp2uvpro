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

    # Test 2: Input is kHz (e.g., 0.675 kHz -> 675 Hz)
    val_khz_ctcss = 0.675
    hz = format_sub_audio_to_hz(val_khz_ctcss)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_khz_ctcss} kHz -> Hz: {hz}, MHz: {mhz}")
    assert hz == 675
    assert mhz == 0.000675

    # Test 3: Input is Hz (e.g., 100 Hz)
    val_hz = 100
    hz = format_sub_audio_to_hz(val_hz)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_hz} Hz -> Hz: {hz}, MHz: {mhz}")
    assert hz == 100
    assert mhz == 0.0001

    # Test 4: Input is Hz (e.g., 1000 Hz)
    val_hz_large = 1000
    hz = format_sub_audio_to_hz(val_hz_large)
    mhz = format_sub_audio_to_mhz(hz)
    print(f"Input: {val_hz_large} Hz -> Hz: {hz}, MHz: {mhz}")
    assert hz == 1000
    assert mhz == 0.001

    print("All tests passed!")

if __name__ == "__main__":
    test_sub_audio()
