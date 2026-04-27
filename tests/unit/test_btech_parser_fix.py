import pytest
from src.converter.btech import BtechParser

def test_btech_parser_with_json_prefix():
    content = 'BWE/BTECH JSON{"chs":[{"n":"Test","tf":"146.520","rf":"146.520","ts":"13180","s":"1","p":"H","m":"FM"}]}'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_btech_parser_with_csv_prefix():
    header = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=0/1=1),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
    content = f'BTECH UV{header}\nTest,146520000,146520000,0,0,H,25000,1,0,0,1,0,0,0,0,0'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_btech_parser_with_json_no_prefix():
    content = '{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_btech_parser_with_csv_no_prefix():
    header = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=0/1=1),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
    content = f'title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=0/1=1),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nTest,146520000,146520000,0,0,H,25000,1,0,0,1,0,0,0,0,0'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_btech_parser_with_csv_prefix():
    content = 'BTECH UVtitle,tx_freq,rx_freq\nTest,146520000,146520000'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_btech_parser_with_json_no_prefix():
    content = '{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_btech_parser_with_csv_no_prefix():
    content = 'title,tx_freq,rx_freq\nTest,146520000,146520000'
    parser = BtechParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0
