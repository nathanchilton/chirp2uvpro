import pandas as pd
import io
from converter.chirp import ChirpGenerator

def test_chirp_generator_flags():
    generator = ChirpGenerator()
    channels = [
        {
            'name': 'Test Channel 1',
            'tx_freq_hz': 462550000,
            'rx_freq_hz': 462550000,
            'tx_sub_audio_hz': 100000,
            'rx_sub_audio_hz': 0,
            'tx_power': 'M',
            'bandwidth_hz': 12500,
            'scan': True,
            'talk_around': True,
            'mute': True,
            'sign': True,
            'tx_dis': True,
            'bclo': True,
            'pre_de_emph_bypass': True,
            'rx_modulation': 'FM',
            'tx_modulation': 'FM'
        },
        {
            'name': 'Test Channel 2',
            'tx_freq_hz': 462550000,
            'rx_freq_hz': 462550000,
            'tx_sub_audio_hz': 0,
            'rx_sub_audio_hz': 0,
            'tx_power': 'H',
            'bandwidth_hz': 25000,
            'scan': False,
            'talk_around': False,
            'mute': False,
            'sign': False,
            'tx_dis': False,
            'bclo': False,
            'pre_de_emph_bypass': False,
            'rx_modulation': 'AM',
            'tx_modulation': 'AM'
        }
    ]
    
    csv_content = generator.generate(channels)
    df = pd.read_csv(io.StringIO(csv_content))
    
    # Check Channel 1
    ch1 = df[df['Name'] == 'Test Channel 1'].iloc[0]
    assert int(ch1['Scan']) == 1
    assert int(ch1['TalkAround']) == 1
    assert int(ch1['Mute']) == 1
    assert int(ch1['Sign']) == 1
    assert int(ch1['TxDis']) == 1
    assert int(ch1['Bclo']) == 1
    assert int(ch1['PreDeEmphBypass']) == 1
    
    # Check Channel 2
    ch2 = df[df['Name'] == 'Test Channel 2'].iloc[0]
    assert int(ch2['Scan']) == 0
    assert int(ch2['TalkAround']) == 0
    assert int(ch2['Mute']) == 0
    assert int(ch2['Sign']) == 0
    assert int(ch2['TxDis']) == 0
    assert int(ch2['Bclo']) == 0
    assert int(ch2['PreDeEmphBypass']) == 0

if __name__ == "__main__":
    test_chirp_generator_flags()
    print("Test passed!")
