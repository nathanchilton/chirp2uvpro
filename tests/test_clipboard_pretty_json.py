import pytest
import json
from src.converter.clipboard import ClipboardParser, ClipboardGenerator

def test_clipboard_roundtrip_pretty_json():
    # Original CLIPBOARD content (Pretty-printed JSON)
    channels_data = {
        "chs": [
            {
                "n": "N5RCA",
                "rf": "146.780",
                "tf": "146.180",
                "ts": 13180,
                "rs": 13180,
                "s": 1,
                "id": 1,
                "p": 0
            }
        ]
    }
    json_content = json.dumps(channels_data, indent=4)
    original_content = f'Copy this text and start BTECH UV{json_content}'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    assert channels[0].name == 'N5RCA'
    assert channels[0].rx_freq_hz == 146780000.0
    assert channels[0].tx_freq_hz == 146180000.0
    assert channels[0].tx_sub_audio_hz == 131.8
    assert channels[0].rx_sub_audio_hz == 131.8
    assert channels[0].scan is True
    assert channels[0].tx_power == '0'
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same    
    assert len(channels_back) == 1
    assert channels_back[0].name == 'N5RCA'
    assert channels_back[0].rx_freq_hz == 146780000.0
    assert channels_back[0].tx_freq_hz == 146180000.0
    assert channels_back[0].tx_sub_audio_hz == 131.8
    assert channels_back[0].rx_sub_audio_hz == 131.8
    assert channels_back[0].scan is True
    assert channels_back[0].tx_power == '0'

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
