import pytest
from src.converter.clipboard import ClipboardParser, ClipboardGenerator

def test_clipboard_roundtrip_data_preservation():
    # Original CLIPBOARD content (abbreviated format)
    # We use a string that is definitely what the parser expects
    original_content = 'Copy this text and start BTECH UV{"chs":[{"n":"N5RCA","rf":"146.780","tf":"146.180","ts":13180,"s":1,"id":1,"p":0}]}'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    assert channels[0]['name'] == 'N5RCA'
    assert channels[0]['rx_freq_hz'] == 146780000.0
    assert channels[0]['tx_freq_hz'] == 146180000.0
    assert channels[0]['tx_sub_audio_hz'] == 13180.0
    assert channels[0]['scan'] is True
    assert channels[0]['tx_power'] == '0'
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same
    assert len(channels_back) == 1
    assert channels_back[0]['name'] == 'N5RCA'
    assert channels_back[0]['rx_freq_hz'] == 146780000.0
    assert channels_back[0]['tx_freq_hz'] == 146180000.0
    assert channels_back[0]['tx_sub_audio_hz'] == 13180.0
    assert channels_back[0]['scan'] is True
    assert channels_back[0]['tx_power'] == '0'

def test_clipboard_roundtrip_with_expanded_keys():
    # This test checks if the roundtrip preserves data even when extra keys are present
    # which is what happens when we convert from CHIRP to CLIPBOARD
    original_content = 'Copy this text and start BTECH UV{"chs":[{"n":"N5CA","rf":"146.780","tf":"146.180","ts":13180,"s":1,"id":1,"p":0,"location":"","rx_freq_hz":146780000.0,"offset_hz":600000.0,"duplex":"+","bandwidth_hz":25000,"rx_sub_audio_hz":0.0,"skip":false,"talk_around":false,"pre_de_emph_bypass":false,"sign":false,"tx_dis":false,"bclo":false,"mute":false,"rx_modulation":"FM","tx_modulation":"FM"}]}'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    
    # 2. Generate CHIRP-style JSON
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same
    assert len(channels_back) == 1
    assert channels_back[0]['name'] == 'N5CA'
    assert channels_back[0]['rx_freq_hz'] == 146780000.0
    assert channels_back[0]['tx_freq_hz'] == 146180000.0
    assert channels_back[0]['tx_sub_audio_hz'] == 13180.0

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])

