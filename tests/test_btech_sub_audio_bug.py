import unittest
from src.converter.btech import BtechParser, BtechGenerator
from src.converter.models import Channel

class TestBtechSubAudioBug(unittest.TestCase):
    def setUp(self):
        self.btech_parser = BtechParser()
        self.btech_generator = BtechGenerator()

    def test_ctcss_sub_audio_regression(self):
        # Testing CTCSS (Hz)
        channels = [
            Channel(
                name='Test CTCSS',
                tx_freq_hz=462000000.0,
                rx_freq_hz=462000000.0,
                tx_sub_audio_hz=1000.0,
                rx_sub_audio_hz=1000.0,
                tx_power='M'
            )
        ]
        btech_content = self.btech_generator.generate(channels)
        # BTECH -> BTECH
        parsed_channels = self.btech_parser.parse(btech_content)
        self.assertEqual(len(parsed_channels), 1)
        self.assertEqual(parsed_channels[0].tx_sub_audio_hz, 1000.0)

    def test_btech_uv_sub_audio_regression(self):
        # Testing BTECH UV format (0.01Hz units)
        # We need to use the prefix to trigger is_btech_uv_format = True
        prefix = "BTECH UV"
        # In BTECH UV format, 100000 (0.01Hz) = 1000 Hz
        # The reference BTECH format uses 0.01Hz units for sub-audio
        # Let's try to generate a CSV that uses the prefix
        # Since BtechGenerator doesn't support the prefix, we'll manually create the content
        content = f"{prefix}\ntitle,location,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\n"
        content += "Test,Loc,462000000,462000000,100000,100000,M,25000,0,0,0,0,0,0,0,FM,FM"
        
        parsed_channels = self.btech_parser.parse(content)
        self.assertEqual(len(parsed_channels), 1)
        # NOTE: This test expects correct 0.01Hz behavior (100000 * 0.01 = 1000 Hz)
        # but the current parser uses Hz scale, producing 100000.0
        # This test will FAIL until T3 fixes the parser to use 0.01Hz scale
        self.assertEqual(parsed_channels[0].tx_sub_audio_hz, 1000.0)

if __name__ == "__main__":
    unittest.main()
