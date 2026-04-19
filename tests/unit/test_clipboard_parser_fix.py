import pytest
from src.converter.clipboard import ClipboardParser

def test_clipboard_parser_with_json_prefix():
    content = 'Copy this text and start BTECH UV{"chs":[{"n":"N5RCA","rf":"146.740","tf":"146.140","ts":13180,"s":1,"id":1,"p":0}]}'
    parser = ClipboardParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0]['name'] == 'N5RCA'
    assert channels[0]['rx_freq_hz'] == 146740000.0
    assert channels[0]['tx_freq_hz'] == 146140000.0
    assert channels[0]['tx_sub_audio_hz'] == 13180.0
    assert channels[0]['scan'] is True
    assert channels[0]['tx_power'] == 'M'

def test_clipboard_parser_with_csv_prefix():
    content = 'BTECH UVtitle,tx_freq,rx_freq\nTest,146520000,146520000'
    parser = ClipboardParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0]['title'] == 'Test'
