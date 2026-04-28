import pytest
from src.converter.mock_repeaterbook import get_mock_repeaters
from src.converter.clipboard import ClipboardGenerator, ClipboardParser
from src.converter.models import Channel
import json

def test_mock_api_to_clipboard_format_validity():
    # 1. Get mock data from "API"
    lat, lon = 34.0522, -118.2437
    repeaters = get_mock_repeaters(lat, lon)
    
    # 2. Convert repeater data to Channel objects
    channels = []
    for r in repeaters:
        # r has 'n' and 'rf'
        # We need to map 'n' to name and 'rf' to rx_freq_hz/tx_freq_hz
        # For simplicity, we'll assume rf is the frequency for both
        channels.append(Channel(
            name=r['n'],
            rx_freq_hz=float(r['rf']) * 1_000_000,
            tx_freq_hz=float(r['rf']) * 1_000_000,
            tx_sub_audio_hz=0.0,
            rx_sub_audio_hz=0.0,
            tx_power='M',
            bandwidth_hz=12500,
            scan=True,
            talk_around=False,
            pre_de_emph_bypass=False,
            sign=False,
            tx_dis=False,
            bclo=False,
            mute=False,
            rx_modulation='FM',
            tx_modulation='FM',
            skip=False
        ))
    
    # 3. Generate clipboard format (JSON)
    generator = ClipboardGenerator(format='json')
    generated_text = generator.generate(channels)
    
    # 4. Verify Prefix
    prefix = "Copy this text and start BTECH UV"
    assert generated_text.startswith(prefix)
    
    # 5. Verify JSON content
    json_part = generated_text[len(prefix):]
    print(f"\nGenerated JSON part: {json_part[:200]}...")
    try:
        data = json.loads(json_part)
    except json.JSONDecodeError as e:
        pytest.fail(f"Generated text does not contain valid JSON: {e}")
    
    assert "chs" in data
    assert isinstance(data["chs"], list)
    assert len(data["chs"]) == len(channels)
    
    # 6. Verify structure matches documentation (example_clipboard_format.txt)
    # The documentation shows keys like 'n', 'rf', 'tf', 'ts', 's', 'id', 'p'
    # We should check that at least the essential keys are present in the generated JSON
    for i, ch_data in enumerate(data["chs"]):
        assert "n" in ch_data
        assert "rf" in ch_data
        # The first repeater in our mock test should match the name we generated
        assert ch_data["n"] == repeaters[i]["n"]
        
    # 7. Ensure it can be parsed back
    parser = ClipboardParser()
    parsed_channels = parser.parse(generated_text)
    assert len(parsed_channels) == len(channels)
    assert parsed_channels[0].name == channels[0].name
    assert parsed_channels[0].rx_freq_hz == pytest.approx(channels[0].rx_freq_hz)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
