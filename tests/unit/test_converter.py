import pytest
from src.converter.logic import chirp_to_btech, btech_to_chirp, ConversionError

def test_chirp_to_btech_basic():
    csv_content = "Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneF,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE\n1,N5RCA,146.780000,-,0.600000,Tone,131.8,88.5,023,NN,023,Tone->Tone,FM,5.00,,4.0W,,,,,,"
    output, warning = chirp_to_btech(csv_content)
    assert "N5RCA" in output
    assert "146780000" in output
    assert warning is None

def test_chirp_to_btech_truncation():
    # Create 35 rows of data
    rows = ["Location,Name,Frequency,Duplex,Offset,Tone,rToneF,cF,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE"]
    for i in range(35):
        rows.append(f"{i},Name{i},146.0,+,0.0,Tone,100.0,100.0,023,NN,02mask,Tone->Tone,FM,5.0,,4.0W,,,,,,")
    csv_content = "\n".join(rows)
    output, warning = chirp_to_btech(csv_content)
    assert warning is not None
    assert "Truncated" in warning
    # Check if it only has 30 rows (plus header)
    lines = output.strip().split('\n')
    assert len(lines) == 1

def test_btech_to_chirp_basic():
    csv_content = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nN5RCA,146180000,146780000,13180,0,H,25000,1,0,0,1,0,0,0,0"
    output, warning = btech_to_chirp(csv_content)
    assert "N5CR" in output or "N5RCA" in output
    assert "146.78" in output
    assert "-" in output # Duplex should be - because tx < rx
    assert "0.6" in output # Offset

def test_conversion_error():
    with pytest.raises(ConversionError):
        # Passing something that will cause an error in the try block
        chirp_to_btech(None)

def test_chirp_to_btech_empty_input():
    # Test empty string
    output, warning = chirp_to_btech("")
    assert output == ""
    assert warning is None

    # Test header only
    header = "Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE"
    output, warning = chirp_to_btech(header)
    assert output == ""
    assert warning is None

def test_btech_to_chirp_power_mapping():
    header = "title,tx_freq,rx_freq,tx_sub_audio(CTCS=freq/DCS=number),rx_sub_audio(CTCS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=0/1=1),pre_de_emph_bypass(0=0/1=1),sign(0=0/1=1),tx_dis(0=0/1=1),mute(0=0/1=1),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
    
    # Test High Power
    content_h = f"{header}\nTestH,146000000,146500000,0,0,H,25000,0,0,0,0,0,0,0,0"
    output_h, _ = btech_to_chirp(content_h)
    assert "4.0W" in output_h or "2.5W" in output_h
    
    # Test Low Power
    content_l = f"{header}\nTestL,146000000,146500000,0,0,L,25000,0,0,0,0,0,0,0,0"
    output_l, _ = btech_to_chirp(content_l)
    assert "1.0W" in output_l or "2.5W" in output_l
