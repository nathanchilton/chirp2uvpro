import pytest
from src.converter.chirp import ChirpParser, ChirpGenerator
from src.converter.btech import BtechParser, BtechGenerator

def test_flag_roundtrip():
    # Original BTECH data with all flags set to True
    btech_content = """BTECH UV
Name,Frequency,Duplex,Offset,Tone,rToneFreq,Power,Scan,TalkAround,Mute,Sign,TxDis,Bclo,PreDeEmphBypass
TestCh,462.55,0,0,Tone,100.0,M,1,1,1,1,1,1,1
"""
    # Note: I'm using 1 for True in BTECH as it's often represented as 1/0 in BTECH CSVs or similar.
    
    print("Starting Round-trip test for flags...")

    # 1. Parse BTECH
    btech_parser = BtechParser()
    channels_from_btech = btech_parser.parse(btech_content)
    print(f"Parsed from BTECH: {channels_from_btech}")

    if not channels_from_btech:
        print("Error: Failed to parse BTECH content")
        return

    # 2. Generate CHIRP from BTECH
    chirp_gen = ChirpGenerator()
    chirp_content = chirp_gen.generate(channels_from_btech)
    print(f"Generated CHIRP:\n{chirp_content}")

    # 3. Parse CHIRP
    chirp_parser = ChirpParser()
    channels_from_chirp = chirp_parser.parse(chirp_content)
    print(f"Parsed from CHIRP: {channels_from_chirp}")

    # 4. Generate BTECH from CHIRP
    btech_gen = BtechGenerator()
    final_btech_content = btech_gen.generate(channels_from_chirp)
    print(f"Generated Final BTECH:\n{final_btech_content}")

    # 5. Verify
    # Let's parse the final BTECH to see what it actually produced
    final_channels = btech_parser.parse(final_btech_content)
    print(f"Parsed Final BTECH: {final_channels}")

    # Check if flags match
    original_ch = channels_from_btech[0]
    final_ch = final_channels[0]

    flags_to_check = ['scan', 'talk_around', 'mute', 'sign', 'tx_dis', 'bclo']
    
    errors = 0
    for flag in flags_to_check:
        if getattr(original_ch, flag) != getattr(final_ch, flag):
            print(f"Mismatch in {flag}: {getattr(original_ch, flag)} != {getattr(final_ch, flag)}")
            errors += 1
    
    if errors == 0:
        print("SUCCESS: Flags preserved!")
    else:
        raise AssertionError(f"FAILURE: {errors} flag mismatches found.")

if __name__ == "__main__":
    test_flag_roundtrip()
