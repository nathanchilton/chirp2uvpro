import unittest
from src.converter.btech import BtechParser

class TestBtechParserSubAudioCSV(unittest.TestCase):
    def test_rx_sub_audio_sync_with_tx_when_rf_missing_in_csv(self):
        parser = BtechParser()
        # CSV content where rf is missing (or 0), so rx_f should become tx_f
        # and rx_sub_audio_hz should also become tx_sub_audio_hz
        # Using a simple CSV format with Hz values
        csv_content = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number)\nTest,462000000.0,0,1000,0"
        channels = parser.parse(csv_content)
        
        self.assertEqual(len(channels), 1)
        ch = channels[0]
        print(f"\nDEBUG: ch.tx_freq_hz={ch.tx_freq_hz}")
        print(f"DEBUG: ch.rx_freq_hz={ch.rx_freq_hz}")
        print(f"DEBUG: ch.tx_sub_audio_hz={ch.tx_sub_audio_hz}")
        print(f"DEBUG: ch.rx_sub_audio_hz={ch.rx_sub_audio_hz}")
        
        self.assertEqual(ch.tx_freq_hz, 462000000.0)
        self.assertEqual(ch.rx_freq_hz, 462000000.0)
        self.assertEqual(ch.tx_sub_audio_hz, 1000.0)
        # Ensure rx_sub_audio_hz is also synced when rf is 0
        self.assertEqual(ch.rx_sub_audio_hz, 1000.0, "rx_sub_audio_hz should sync with tx_sub_audio_hz when rf is 0 in CSV")

if __name__ == "__main__":
    unittest.main()


