import unittest
from src.converter.btech import BtechParser

class TestBtechParserSubAudio(unittest.TestCase):
    def test_rx_sub_audio_sync_with_tx_when_rf_missing(self):
        parser = BtechParser()
        # JSON content where rf is missing, so rx_f should become tx_f
        # and rx_sub_audio_hz should also become tx_sub_audio_hz
        json_content = '{"chs": [{"n": "Test", "tf": 462000000, "t": 1000, "ts": 1000}]}'
        channels = parser.parse(json_content)
        
        self.assertEqual(len(channels), 1)
        ch = channels[0]
        self.assertEqual(ch['tx_freq_hz'], 462000000.0)
        self.assertEqual(ch['rx_freq_hz'], 462000000.0)
        self.assertEqual(ch['tx_sub_audio_hz'], 1000)
        # If the bug exists, this will be 0 instead of 1000
        self.assertEqual(ch['rx_sub_audio_hz'], 1000, "rx_sub_audio_hz should sync with tx_sub_audio_hz when rf is missing")

if __name__ == "__main__":
    unittest.main()
