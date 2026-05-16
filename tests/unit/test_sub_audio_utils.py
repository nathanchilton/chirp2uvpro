import pandas as pd
from src.converter.utils import (
    format_sub_audio_to_hz,
    format_sub_audio_to_mhz,
    format_sub_audio_to_units,
    format_freq_to_hz,
    format_freq_to_mhz
)

def test_sub_audio_to_hz():
    # Test 1: Input is kHz (e.g., 0.1 kHz -> 100 Hz)
    val_khz = 0.1
    hz = format_sub_audio_to_hz(val_khz, scale='kHz')
    assert hz == 100.0

    # Test 2: Input is kHz (e.g., 0.1318 kHz -> 131.8 Hz)
    val_khz_ctcss = 0.1318
    hz = format_sub_audio_to_hz(val_khz_ctcss, scale='kHz')
    assert hz == 131.8

    # Test 3: Input is DCS (e.g., 23)
    val_dcs = 23
    hz = format_sub_audio_to_hz(val_dcs)
    assert hz == 23.0

    # Test 4: Input is an invalid value (e.g., "abc")
    val_invalid = "abc"
    hz = format_sub_audio_to_hz(val_invalid)
    assert hz == 0.0

    # Test 5: Input is Hz (e.g., 100 Hz)
    val_hz = 100
    hz = format_sub_audio_to_hz(val_hz)
    assert hz == 100.0

def test_sub_audio_to_mhz():
    # Test 1: Input is kHz (e.g., 0.1 kHz -> 100 Hz -> 0.0001 MHz)
    val_khz = 0.1
    hz = format_sub_audio_to_hz(val_khz, scale='kHz')
    mhz = format_sub_audio_to_mhz(hz)
    assert mhz == 0.0001

    # Test 2: Input is DCS (e.g., 2rads -> 23)
    val_dcs = 23
    hz = format_sub_audio_to_hz(val_dcs)
    mhz = format_sub_audio_to_mhz(hz)
    assert mhz == 0.000023

def test_sub_audio_to_units():
    # Test 1: Input is 131.8 Hz, unit is 0.01Hz -> 13180
    hz = 131.8
    units = format_sub_audio_to_units(hz, unit_scale='0.01Hz')
    assert units == 13180

    # Test 2: Input is 131.8 Hz, unit is 0.1Hz -> 1318
    units = format_sub_audio_to_units(hz, unit_scale='0.1Hz')
    assert units == 1318

    # Test 3: Input is 131.8 Hz, unit is Hz -> 132 (rounded)
    units = format_sub_audio_to_units(hz, unit_scale='Hz')
    assert units == 132

def test_freq_to_hz():
    # Test 1: Input is MHz (e.g., 146.78 MHz -> 146780000 Hz)
    val_mhz = 146.78
    hz = format_freq_to_hz(val_mhz, scale='MHz')
    assert hz == 146780000.0

    # Test 2: Input is kHz (e.g., 146.78 kHz -> 146780 Hz)
    val_khz = 146.78
    hz = format_freq_to_hz(val_khz, scale='kHz')
    assert hz == 146780.0

    # Test 3: Input is Hz (e.g., 146.78 Hz -> 146.78 Hz)
    val_hz = 146.78
    hz = format_freq_to_hz(val_hz, scale='Hz')
    assert hz == 146.78

def test_freq_to_mhz():
    # Test 1: Input is MHz (e.g., 146.78 MHz -> 146.78 MHz)
    val_mhz = 146.78
    mhz = format_freq_to_mhz(val_mhz, scale='MHz')
    assert mhz == 146.78

    # Test 2: Input is kHz (e.g., 146.78 kHz -> 0.14678 MHz)
    val_khz = 146.78
    mhz = format_freq_to_mhz(val_khz, scale='kHz')
    assert mhz == 0.14678

    # Test 3: Input is Hz (e.g., 146.78 Hz -> 0.00014678 MHz)
    val_hz = 146.78
    mhz = format_freq_to_mhz(val_hz, scale='Hz')
    assert mhz == 0.00014678
