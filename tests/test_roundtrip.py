import unittest
import io
import pytest
from src.converter.btech import BtechParser, BtechGenerator
from src.converter.chirp import ChirpParser, ChirpGenerator
from src.converter.models import Channel

class TestLosslessRoundTrip(unittest.TestCase):
    def setUp(self):
        self.btech_parser = BtechParser()
        self.btech_generator = BtechGenerator()
        self.chirp_parser = ChirpParser()
        self.chirp_generator = ChirpGenerator()

    def test_btech_to_chirp_to_btech_roundtrip(self):
        # Read BTECH CSV from reference file
        with open('tests/data/example_btech_format.csv', 'r') as f:
            btech_content = f.read()
        
        # BTECH -> Channels
        channels = self.btech_parser.parse(btech_content)
        self.assertGreater(len(channels), 0)
        
        # Channels -> CHIRP
        chirp_content = self.chirp_generator.generate(channels)
        
        # CHIRP -> BTECH
        channels_back = self.btech_parser.parse(chirp_content)
        self.assertEqual(len(channels), len(channels_back))
        
        for original, back in zip(channels, channels_back):
            self.assertEqual(original.tx_freq_hz, back.tx_freq_hz)
            self.assertEqual(original.rx_freq_hz, back.rx_freq_hz)
            self.assertEqual(original.name, back.name)


if __name__ == "__main__":
    unittest.main()
