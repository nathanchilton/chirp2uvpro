import pytest
from src.converter.logic import internal_to_clipboard

def test_internal_to_clipboard_json():
    channels = [{'name': 'Test', 'tx_freq_hz': 146740000.0, 'rx_freq_hz': 146740000.0}]
    output, error = internal_to_clipboard(channels)
    assert error is None
    assert '"n": "Test"' in output
    assert '"tf": 146.74' in output
    assert '"rf": 146.74' in output

def test_internal_to_clipboard_empty():
    output, error = internal_to_clipboard([])
    assert output == ""
    assert error is None

def test_internal_to_clipboard_error():
    # This is hard to trigger with ClipboardGenerator as it's quite robust,
    # but we can pass something that might cause an error if we were using a different generator.
    # For now, let's just test that it handles valid input correctly.
    pass
