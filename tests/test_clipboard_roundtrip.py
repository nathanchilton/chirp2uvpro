import pytest
from src.converter.clipboard import ClipboardParser, ClipboardGenerator

def test_clipboard_roundtrip_data_preservation():
    # Original CLIPBOARD content (abbrevi
    original_content = 'Copy this text and start BTECH UV{"chs":[{"n":"N5RCA","rf":"146.780","tf":"146.180","ts":13180,"rs":13180,"s":1,"id":1,"p":0}]}'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    assert channels[0].name == 'N5RCA'
    assert channels[0].rx_freq_hz == 146780000.0
    assert channels[0].tx_freq_hz == 146180000.0
    assert channels[0].tx_sub_audio_hz == 13180.0
    assert channels[0].rx_sub_audio_hz == 13180.0
    assert channels[0].scan is True
    assert channels[0].tx_power == '0'
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the    
    assert len(channels_back) == 1
    assert channels_back[0].name == 'N5RCA'
    assert channels_back[0].rx_freq_hz == 146780000.0
    assert channels_back[0].tx_freq_hz == 146180000.0
    assert channels_back[0].tx_sub_audio_hz == 13180.0
    assert channels_back[0].rx_sub_audio_hz == 13180.0
    assert channels_back[0].scan is True
    assert channels_back[0].tx_power == '0'

def test_clipboard_roundtrip_csv():
    # Original CLIPBOARD content (CSV-like format)
    original_content = 'Copy this text and start BTECH UVname,tx_freq_hz,rx_freq_hz\nTestCh,146.52,146.52'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    assert channels[0].name == 'TestCh'
    assert channels[0].rx_freq_hz == 146520000.0
    assert channels[0].tx_freq_hz == 146520000.0
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same
    assert len(channels_back) == 1
    assert channels_back[0].name == 'TestCh'
    assert channels_back[0].rx_freq_hz == 146520000.0
    assert channels_back[0].tx_freq_hz == 146520000.0

def test_clipboard_roundtrip_csv_subaudio():
    # Test CSV with sub-audio frequencies
    # Use the full format produced by the generator
    original_content = 'Copy this text and start BTECH UVname,tx_freq_hz,rx_freq_hz,tx_sub_audio_hz,rx_sub_audio_hz\nTestCh,146.52,146.52,0.1318,0.1318'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    assert channels[0].name == 'TestCh'
    assert channels[0].tx_freq_hz == 146520000.0
    assert channels[0].rx_sub_audio_hz == 131800.0
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same
    assert len(channels_back) == 1
    assert channels_back[0].name == 'TestCh'
    assert channels_back[0].tx_freq_hz == 146520000.0
    assert channels_back[0].rx_sub_audio_hz == 131800.0

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
