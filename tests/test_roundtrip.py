import unittest
import io
from src.converter.btech import BtechParser, BtechGenerator
from src.converter.chirp import ChirpParser, ChirpGenerator

class TestLosslessRoundTrip(unittest.TestCase):
    def setUp(self):
        self.btech_parser = BtechParser()
        self.btech_generator = BtechGenerator()
        self.chirp_parser = ChirpParser()
        self.chirp_generator = ChirpGenerator()

    def test_btech_to_chirp_to_btech_roundtrip(self):
        # Create a BTECH CSV
        channels = [
            {
                'name': 'Test Channel',
                'location': 'Test Loc',
                'tx_freq_hz': 462000000.0,
                'rx_freq_hz': 462000000.0,
                'tx_sub_audio_hz': 1000,
                'rx_sub_audio_hz': 1000,
                'tx_power': 'M',
                'bandwidth_hz': 25000,
                'scan': True,
                'talk_around': False,
                'pre_de_emph_bypass': False,
                'sign': False,
                'tx_dis': False,
                'bclo': False,
                'mute': False,
                'rx_modulation': 'AM',
                'tx_modulation': 'FM',
                'skip': False
            }
        ]
        btech_content = self.btech_generator.generate(channels)
        
        # BTECH -> CHIRP
        chirp_channels = self.chirp_parser.parse(btech_content)
        self.assertEqual(len(chirp_channels), 1)
        self.assertEqual(chirp_channels[0]['tx_freq_hz'], 462000000.0)
        self.assertEqual(chirp_channels[0]['tx_sub_audio_hz'], 1000)
        self.assertEqual(chirp_channels[0]['name'], 'Test Channel')
        self.assertEqual(chirp_channels[0]['skip'], False)
        self.assertEqual(chirp_channels[0]['location'], 'Test Loc')
        
        chirp_content = self.chirp_generator.generate(chirp_channels)
        
        # CHIRP -> BTECH
        btech_channels_back = self.btech_parser.parse(chirp_content)
        self.assertEqual(len(btech_channels_back), 1)
        self.assertEqual(btech_channels_back[0]['tx_freq_hz'], 462000000.0)
        self.assertEqual(btech_channels_back[0]['tx_sub_audio_hz'], 1000)
        self.assertEqual(btech_channels_back[0]['name'], 'Test Channel')
        self.assertEqual(btech_channels_back[0]['skip'], '0')
        self.assertEqual(btech_channels_back[0]['location'], 'Test Loc')

if __name__ == "__main__":
    unittest.main()
