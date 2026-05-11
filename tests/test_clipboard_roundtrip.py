import pytest
from src.converter.clipboard import ClipboardParser, ClipboardGenerator

def test_clipboard_roundtrip_data_preservation():
    # Read original CLIPBOARD content from reference file
    with open('tests/data/example_clipboard_format.txt', 'r') as f:
        original_content = f.read()
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    print(f"DEBUG: Found {len(channels)} channels")
    for c in channels:
        print(f"DEBUG: Channel: {c.name}, RX: {c.rx_freq_hz}, TX: {c.tx_freq_hz}, RX_SUB: {c.rx_sub_audio_hz}, TX_SUB: {c.tx_sub_audio_hz}")
    assert len(channels) > 0
    # Check a few known channels from the reference file
    # N5RCA: rf:146.780, tf:146.180, ts:13180
    found_n5rca = any(c.name == 'N5RCA' and c.rx_freq_hz == 146780000.0 and c.tx_freq_hz == 146180000.0 and c.tx_sub_audio_hz == 131.8 for c in channels)
    assert found_n5rca
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same
    assert len(channels_back) == len(channels)
    # Check a few known channels again
    found_n5rca_back = any(c.name == 'N5RCA' and c.rx_freq_hz == 146780000.0 and c.tx_freq_hz == 146180000.0 and c.tx_sub_audio_hz == 131.8 for c in channels_back)
    assert found_n5rca_back

def test_clipboard_roundtrip_csv():
    # Original CLIPBOARD content (CSV-like format)
    original_content = 'Copy this text and start BTECH UVname,tx_freq_hz,rx_freq_hz\nTestCh,146520000,146520000'
    
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
    original_content = 'Copy this text and start BTECH UVname,tx_freq_hz,rx_freq_hz,tx_sub_audio_hz,rx_sub_audio_hz\nTestCh,146520000,146520000,131.8,131.8'
    
    parser = ClipboardParser()
    generator = ClipboardGenerator(format='json')
    
    # 1. Parse the original content
    channels = parser.parse(original_content)
    assert len(channels) == 1
    assert channels[0].name == 'TestCh'
    assert channels[0].tx_freq_hz == 146520000.0
    assert channels[0].tx_sub_audio_hz == 131.8
    assert channels[0].rx_sub_audio_hz == 131.8
    
    # 2. Generate CHIRP-style JSON from the parsed channels
    generated_content = generator.generate(channels)
    
    # 3. Parse the generated content back
    channels_back = parser.parse(generated_content)
    
    # 4. Verify the data is still the same
    assert len(channels_back) == 1
    assert channels_back[0].name == 'TestCh'
    assert channels_back[0].tx_freq_hz == 146520000.0
    assert channels_back[0].tx_sub_audio_hz == 131.8
    assert channels_back[0].rx_sub_audio_hz == 131.8

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
