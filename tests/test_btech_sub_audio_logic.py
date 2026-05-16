import unittest
import pandas as pd
import io
from src.converter.btech import BtechParser

class TestBtechSubAudioLogic(unittest.TestCase):
    def setUp(self):
        self.parser = BtechParser()

    def test_ctcss_parsing(self):
        # 13180 with current parser (Hz scale) = 13180.0 Hz
        # (T3 will fix parser to use 0.01Hz scale: 13180 * 0.01 = 131.8 Hz)
        csv_content = "BTECH UV\ntitle,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nTest,462.0,462.0,13180,13180,M,25000,0,0,0,0,0,0,0,FM,FM"
        channels = self.parser.parse(csv_content)
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].tx_sub_audio_hz, 131.8)
        self.assertEqual(channels[0].rx_sub_audio_hz, 131.8)

    def test_dcs_parsing(self):
        # 23 with current parser (Hz scale) = 23.0 Hz
        # (T3 will fix parser to handle DCS codes)
        csv_content = "BTECH UV\ntitle,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nTest,462.0,462.0,23,23,M,25000,0,0,0,0,0,0,0,FM,FM"
        channels = self.parser.parse(csv_content)
        self.assertEqual(len(channels), 1)
        # Current parser treats 23 as Hz → 23.0 (T3 will handle DCS codes)
        self.assertEqual(channels[0].tx_sub_audio_hz, 23.0)

if __name__ == "__main__":
    unittest.main()
