import pytest
from src.converter.btech import BtechParser
from src.converter.models import Channel

def test_btech_duplex_inference_with_offset():
    # Reference BTECH format: title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)
    # No duplex,offset,location,skip columns. Frequencies in Hz.
    # Since the BTECH format has no duplex/offset columns, duplex is inferred from tx_freq vs rx_freq.
    csv_content = (
        "BTECH UV\n"
        "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\n"
        "Test Channel,146180000,147180000,0,0,M,25000,0,0,0,0,0,0,0,FM,FM"
    )
    parser = BtechParser()
    channels = parser.parse(csv_content)
    
    assert len(channels) == 1
    ch = channels[0]
    
    # Since offset is 1MHz (1000000 Hz) and duplex is empty, it should infer '+'
    # and rx_freq_hz should be 146.18 MHz + 1 MHz = 147.18 MHz
    assert ch.duplex == '+'
    assert ch.rx_freq_hz == 147180000.0

if __name__ == "__main__":
    pytest.main([__file__])
