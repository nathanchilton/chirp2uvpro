import sys
import os

# Add src to sys.path so we can import the module
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src/converter'))

from converter.logic import btech_to_chirp

def test_csv_with_prefix():
    content = 'BTECH UVtitle,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nTest,146520000,14_6520000,0,0,M,25000,0,0,0,0,0,0,0,FM,FM'
    # Wait, I have a typo in my frequency in the test content above. 14_6520000
    # Let me fix it.
    content = 'BTECH UVtitle,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)\nTest,146520000,146520000,0,0,M,25000,0,0,0,0,0,0,0,FM,FM'
    print(f"Testing content: {content}")
    output, error = btech_to_chirp(content)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Output:\n{output}")
    assert "Test" in output
    assert "146.52" in output

if __name__ == "__main__":
    try:
        test_csv_with_prefix()
        print("CSV test passed!")
    except Exception as e:
        print(f"CSV test failed: {e}")
        sys.exit(1)
