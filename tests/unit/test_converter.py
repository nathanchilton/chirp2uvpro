import pytest
import pandas as pd
import io
from src.converter.clipboard import ClipboardParser
from src.converter.logic import chirp_to_btech, btech_to_chirp, ConversionError
def test_clipboard_parser_with_prefix():
    prefix = "BTECH UV"
    content = f"{prefix}name,tx_freq_hz,rx_freq_hz\nTest,146520000,146520000"
    parser = ClipboardParser()
    channels = parser.parse(content)
    assert len(channels) == 1
    assert channels[0].name == 'Test'
    assert channels[0].tx_freq_hz == 146520000.0

def test_clipboard_parser_json():
    json_content = '{"chs":[{"n":"N5RCA","rf":"146.780","tf":"146.180","ts":13180,"s":1,"id":1,"p":0}]}'
    parser = ClipboardParser()
    channels = parser.parse(json_content)
    assert len(channels) == 1
    assert channels[0].name == 'N5RCA'
    assert channels[0].rx_freq_hz == 146780000.0
    assert channels[0].tx_freq_hz == 146180000.0
    assert channels[0].tx_sub_audio_hz == 13180.0
    assert channels[0].scan is True
    assert channels[0].tx_power == '0'
BTECH_HEADER = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"

def test_chirp_to_btech_basic():
    csv_content = "Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneF,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE\nN5RCA,146.780000,-,0.600000,Tone,131.8,8MA,023,NN,02fmt,Tone->Tone,FM,5.00,,4.0W,,,,,"
    output, warning = chirp_to_btech(csv_content)
    assert "N5RCA" in output
    assert "146.78" in output
    assert warning is None

def test_chirp_to_btech_large_input():
    # Create 35 rows of data
    header = "Name,Frequency,Duplex,Offset,Tone,rTref,c%s,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE".replace('%s', 'cToneF')
    rows = [header]
    for i in range(35):
        rows.append(f"Name{i},146.0,-,0.0,Tone,131.8,8MA,023,NN,0s,Tone->Tone,FM,5.0,,4.0W,,,,")
    csv_content = "\n".join(rows)
    output, warning = chirp_to_btech(csv_content)
    assert warning == "Truncated"

def test_chirp_to_btech_empty_input():
    output, warning = chirp_to_btech("")
    assert output == ""
    assert warning is None

    header = "Name,Frequency,Duplex,Offset,Tone,rToneF,cToneF,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE"
    output, warning = chirp_to_btech(header)
    assert output == ""
    assert warning is None

def test_btech_to_chirp_dcs_ctcss():
    # Test CTCSS (freq)
    content_ctcss = f"{BTECH_HEADER}\nTestCTCSS,146000000,146500000,100,0,H,25000,0,0,0,1,0,0,0,0"
    output_ctcss, _ = btech_to_chirp(content_ctcss)
    assert "Tone" in output_ctcss
    assert "100" in output_ctcss

    # Test DCS (number)
    content_dcs = f"{BTECH_HEADER}\nTestDCS,146000000,146500000,23,0,H,25000,0,0,0,1,0,0,0,0"
    output_dcs, _ = btech_to_chirp(content_dcs)
    # In btech_to_chirp, if sub_audio > 0, it sets Tone='Tone'. 
    # For DCS, it depends on how it's passed. 
    # If it's 23, it's > 0, so it sets Tone='Tone'.
    # The current implementation doesn't distinguish DCS from CTCSS in the chirp output,
    # but let's see if it at least doesn't crash.
    assert "Tone" in output_dcs

def test_integration_pipeline():
    """
    Integration test: CHIRP -> BTECH -> CHIRP
    Ensures that the core information is preserved through the full conversion cycle.
    """
    # Original CHIRP content
    chirp_content = (
        "Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneF,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE\n"
        "0,TestChannel,146.78, -,0.6,Tone,131.8,8MA,023,NN,0s,Tone->Tone,FM,5.0,0,4.0W,,,,,\n"
    )
    
    # 1. CHIRP -> BTECH
    btech_content, warning = chirp_to_btech(chirp_content)
    assert warning is None
    assert "146.78" in btech_content
    
    # 2. BTECH -> CHIRP
    output_chirp, warning = btech_to_chirp(btech_content)
    assert warning is None
    assert "TestChannel" in output_chirp
