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

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
