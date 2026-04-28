import pytest
from src.converter.mock_repeaterbook import get_mock_repeaters

def test_get_mock_repeater_count():
    """Test that get_mock_repeaters returns exactly 30 items."""
    repeaters = get_mock_repeaters(34.0522, -118.2437)
    assert len(repeaters) == 30

def test_get_mock_repeater_keys():
    """Test that each repeater object has the required keys."""
    repeaters = get_mock_repeaters(34.0522, -118.2437)
    required_keys = {"n", "rf", "tf", "ts", "rs"}
    for repeater in repeaters:
        assert required_keys.issubset(repeater.keys())

def test_get_mock_repeater_ranges():
    """Test that frequencies and sub-audio are within expected ranges."""
    repeaters = get_mock_repeaters(34.0522, -118.2437)
    for repeater in repeaters:
        # Frequency range: 144.0 to 148.0 MHz
        assert 144.0 <= repeater["rf"] <= 148.0
        assert 144.0 <= repeater["tf"] <= 148.0
        # Sub-audio range: 67.0 to 250.0 Hz
        assert 67.0 <= repeater["ts"] <= 250.0
        assert 67.0 <= repeater["rs"] <= 250.0

def test_get_mock_repeater_deterministic():
    """Test that get_mock_repeaters is deterministic for the same location."""
    lat, lon = 34.0522, -118.2437
    repeaters1 = get_mock_repeaters(lat, lon)
    repeaters2 = get_mock_repeaters(lat, lon)
    assert repeaters1 == repeaters2

def test_get_mock_repeater_different_locations():
    """Test that get_mock_repeaters produces different results for different locations."""
    lat1, lon1 = 34.0522, -118.2437
    lat2, lon2 = 40.7128, -74.0060
    repeaters1 = get_mock_repeaters(lat1, lon1)
    repeaters2 = get_mock_repeaters(lat2, lon2)
    assert repeaters1 != repeaters2
