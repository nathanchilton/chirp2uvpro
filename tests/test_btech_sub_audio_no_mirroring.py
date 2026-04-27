import pandas as pd
import io
from src.converter.btech import BtechParser

def test_btech_sub_audio_no_mirroring():
    # JSON content for BtechParser._parse_channel_append
    # ts (tx_sub_audio) = 100.0
    # dt (rx_sub_audio) = 200.0
    json_content = """
    [
        {
            "n": "Test Channel",
            "tf": 462550000,
            "rf": 462550000,
            "ts": 100000,
            "dt": 200000,
            "p": "M",
            "s": "1",
            "ta": "0",
            "m": "0",
            "si": "0",
            "td": "0",
            "bc": "0",
            "mb": "0"
        }
    ]
    """
    parser = BtechParser()
    channels = parser.parse(json_content)
    
    if not channels:
        raise Exception("Failed to parse JSON content")
        
    ch = channels[0]
    
    print(f"Parsed TX sub-audio: {ch.tx_sub_audio_hz} Hz")
    print(f"Parsed RX sub-audio: {ch.rx_sub_audio_hz} Hz")
    
    assert ch.tx_sub_audio_hz == 100000
    assert ch.rx_sub_audio_hz == 200000, f"Mirroring detected! RX sub-audio is {ch.rx_sub_audio_hz} Hz instead of 200000 Hz"

if __name__ == "__main__":
    test_btech_sub_audio_no_mirroring()
    print("Test passed!")
