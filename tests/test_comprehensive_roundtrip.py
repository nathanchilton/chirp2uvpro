import pandas as pd
import io
import pytest
from converter.chirp import ChirpParser, ChirpGenerator
from converter.btech import BtechParser, BtechGenerator

def test_comprehensive_roundtrip():
    # A comprehensive BTECH data set
    btech_content = """BTECH UV
Name,Frequency,Duplex,Offset,Tone,rToneFreq,Power,Scan,TalkAround,Mute,Sign,TxDis,Bclo,PreDeEmphBypass
TestCh1,462.55,0,0,Tone,100.0,M,1,1,1,1,1,1,1
TestCh2,462.55,0,0,None,0,H,0,0,0,0,0,0,0
TestCh3,462.55,0,0,Tone,200.0,L,1,0,1,0,1,0,1
TestCh4,146.74,1,0.001,Tone,600.0,M,0,0,1,0,0,0,1
TestCh5,440.0,0,0,None,0,H,1,1,0,1,0,1,0
"""
    
    print("Starting Comprehensive Round-trip test...")

    # 1. Parse BTECH
    btech_parser = BtechParser()
    channels_from_btech = btech_parser.parse(btech_content)
    
    if not channels_from_btech:
        raise AssertionError("Error: Failed to parse BTECH content")
    
    # 2. Generate CHIRP from BTECH
    chirp_gen = ChirpGenerator()
    chirp_content = chirp_gen.generate(channels_from_btech)
    
    # 3. Parse CHIRP
    chirp_parser = ChirpParser()
    channels_from_chirp = chirp_parser.parse(chirp_content)
    
    # 4. Generate BTECH from CHIRP
    btech_gen = BtechGenerator()
    final_btech_content = btech_gen.generate(channels_from_chirp)
    
    # 5. Verify
    final_channels = btech_parser.parse(final_btech_content)
    
    assert len(channels_from_btech) == len(final_channels)
    
    for i in range(len(channels_from_btech)):
        orig = channels_from_btech[i]
        final = final_channels[i]
        
        # Check all critical fields
        assert orig['name'] == final['name']
        # Use approx for floats
        assert orig['tx_freq_hz'] == pytest.approx(final['tx_freq_hz'])
        assert orig['rx_freq_hz'] == pytest.approx(final['rx_freq_hz'])
        assert orig['tx_sub_audio_hz'] == pytest.approx(final['tx_sub_audio_hz'])
        assert orig['rx_sub_audio_hz'] == pytest.approx(final['rx_sub_audio_hz'])
        assert orig['tx_power'] == final['tx_power']
        assert orig['scan'] == final['scan']
        assert orig['talk_around'] == final['talk_around']
        assert orig['mute'] == final['mute']
        assert orig['sign'] == final['sign']
        assert orig['tx_dis'] == final['tx_dis']
        assert orig['bclo'] == final['bclo']
        assert orig['pre_de_emph_bypass'] == final['pre_de_emph_bypass']

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
