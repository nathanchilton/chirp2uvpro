import pytest
import json
from src.converter.parsers.api_import import ApiImportParser
from src.converter.models import Channel

def test_api_import_parser_success():
    parser = ApiImportParser()
    json_content = json.dumps({
        "repeaters": [
            {
                "n": "Test Repeater 1",
                "rf": 146.52,
                "tf": 146.52,
                "ts": 100.0,
                "rs": 100.0
            },
            {
                "n": "Test Repeater 2",
                "rf": 147.00,
                "tf": 147.50,
                "ts": 123.0,
                "rs": 123.0
            }
        ]
    })
    
    channels = parser.parse(json_content)
    
    assert len(channels) == 2
    
    # Test first repeater (no duplex)
    ch1 = channels[0]
    assert ch1.name == "Test Repeater 1"
    assert ch1.rx_freq_hz == 146520000.0

    assert ch1.tx_freq_hz == 146520000.0
    assert ch1.tx_sub_audio_hz == 100.0
    assert ch1.rx_sub_audio_hz == 100.0
    assert ch1.duplex == 'none'
    assert ch1.offset_hz == 0.0

    # Test second repeater (duplex)
    ch2 = channels[1]
    assert ch2.name == "Test Repeater 2"
    assert ch2.rx_freq_hz == 147000000.0
    assert ch2.tx_freq_hz == 147500000.0
    assert ch2.tx_sub_audio_hz == 123.0
    assert ch2.rx_sub_audio_hz == 123.0
    assert ch2.duplex == '-'
    assert ch2.offset_hz == 500000.0

def test_api_import_parser_empty():
    parser = ApiImportParser()
    assert parser.parse("") == []
    assert parser.parse("{}") == []
    assert parser.parse(json.dumps({"repeaters": "not a list"})) == []

def test_api_import_parser_invalid_json():
    parser = ApiImportParser()
    assert parser.parse("invalid json") == []

def test_api_import_parser_malformed_item():
    parser = ApiImportParser()
    json_content = json.dumps({
        "repeaters": [
            {
                "n": "Malformed Repeater",
                # Missing rf, tf, etc.
            },
            {
                "n": "Good Repeater",
                "rf": 146.52,
                "tf": 146.52,
                "ts": 100.0,
                "rs": 100.0
            }
        ]
    })
    channels = parser.parse(json_content)
    # The parser uses a try-except block inside the loop, so it should skip the malformed one
    assert len(channels) == 1
    assert channels[0].name == "Good Repeater"
