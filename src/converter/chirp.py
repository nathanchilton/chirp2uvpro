import pandas as pd
import io
from typing import List
from .base import BaseParser, BaseGenerator
from .models import Channel
from .utils import (
    format_freq_to_hz,
    format_freq_to_mhz,
    format_sub_audio_to_hz,
    format_power_to_chirp,
    normalize_power,
    is_true
)

class ChirpParser(BaseParser):
    def parse(self, content: str | tuple[str, str | None]) -> List[Channel]:
        if isinstance(content, tuple):
            content = content[0]
        if not content:
            return []
        
        # Strip known prefixes
        prefixes = ["BWE/BCMS JSON", "BWE/BTECH CSV", "B1TECH UV", "BTECH UV", "BWE/BCR JSON", "BWE/BTECH CSV"]
        freq_scale = 'MHz'
        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].lstrip()
                if "BTECH" in prefix or "B1TECH" in prefix:
                    freq_scale = 'Hz'
                break
        
        try:
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []
            
            channels = []
            for _, row in df.iterrows():
                ch = Channel()
                
                # Helper to get value from multiple possible columns
                def get_val(keys, default=0):
                    for k in keys:
                        if k in row and pd.notna(row[k]):
                            return row[k]
                    return default

                ch.name = str(get_val(['Name', 'title', 'name'], ''))
                ch.location = str(get_val(['Location', 'location', 'loc'], ''))
                
                tx_f_val = get_val(['Frequency', 'tx_freq', 'rot_freq', 'tx'], 0)
                ch.tx_freq_hz = float(format_freq_to_hz(tx_f_val, scale=freq_scale))
                
                rx_f_val = get_val(['rx_freq', 'rx_frequency', 'rx'], None)
                rx_f_val_hz = float(format_freq_to_hz(rx_f_val, scale=freq_scale)) if rx_f_val is not None else 0.0
                duplex = str(get_val(['Duplex'], 'none')).strip()
                offset_val = get_val(['Offset'], 0)
                offset_hz = float(format_freq_to_hz(offset_val, scale=freq_scale))
                
                if rx_f_val_hz > 0:
                    ch.rx_freq_hz = rx_f_val_hz
                else:
                    if duplex == '-':
                        ch.rx_freq_hz = ch.tx_freq_hz - offset_hz
                    elif duplex:
                        pass



                
                # Bandwidth
                bw_val = get_val(['TStep', 'bandwidth', 'bandwidth_hz', 'bandwidth(12500/25000)'], 25000.0)
                try:
                    if bw_val < 3000: # Assumes kHz
                        ch.bandwidth_hz = int(float(bw_val) * 1000)
                    else: # Assumes Hz
                        ch.bandwidth_hz = int(float(bw_val))
                except:
                    ch.bandwidth_hz = 25000
                
                # Sub-audible tones
                r_tone = get_val(['rToneFreq', 'ctonef', 'ctost', 'tx_sub_io', 'tx_sub_audio', 'rx_sub_audio', 'tx_sub_audio(CTCSS=freq/DCS=number)', 'rx_sub_audio(CTCSS=freq/DCS=number)'], 0)
                ch.tx_sub_audio_hz = float(format_sub_audio_to_hz(r_tone, scale='Hz')) if r_tone else 0.0
                
                rx_sub_val = get_val(['cToneF', 'cToneFreq', 'rx_sub_audio', 'ctcss', 'tx_sub_audio', 'rx_sub_audio(CTCSS=freq/DCS=number)', 'tx_sub_audio(CTCSS=freq/DCS=number)'], 0)
                ch.rx_sub_audio_hz = float(format_sub_audio_to_hz(rx_sub_val, scale='Hz')) if rx_sub_val else 0.0
                
                tx_p_val = get_val(['Power', 'tx_perm', 'p'], 'M')
                ch.tx_power = tx_p_val
                ch.skip = is_true(get_val(['Skip', 'skip'], False))
                
                # Handle flags
                for flag in ['scan', 'talk_around', 'pre_de_emph_bypass', 'sign', 'tx_dis', 'bclo', 'mute']:
                    col_name = None
                    for variant in [flag, flag.replace('_', '').capitalize(), flag.replace('_', ' ').title().replace(' ', ''), 'PreDeEmphBypass']:
                        if variant in df.columns:
                            col_name = variant
                            break
                    if col_name:
                        setattr(ch, flag, is_true(get_val([col_name], False)))
                    else:
                        setattr(ch, flag, False)
                
                # Modulation
                rx_mod_val = get_val(['Mode', 'rx_modulation', 'rx_mode'], 'FM')
                ch.rx_modulation = 'FM' if str(rx_mod_val).upper() in ['F', 'FM'] else 'AM'
                
                tx_mod_val = get_val(['tx_mode', 'tx_modulation', 'Mode'], 'FM')
                ch.tx_modulation = 'FM' if str(tx_mod_val).upper() in ['F', 'FM'] else 'AM'
                
                channels.append(ch)
            
            return channels
        except Exception as e:
            print(f"Error parsing Chirp CSV: {e}")
            return []

class ChirpGenerator(BaseGenerator):
    def generate(self, channels: List[Channel]) -> tuple[str, str | None]:
        if not channels:
            return "", None
            
        rows = []
        for ch in channels:
            ch_row = {}
            ch_row['Name'] = ch.name
            ch_row['Location'] = ch.location
            
            tx_f_hz = ch.tx_freq_hz
            ch_row['Frequency'] = format_freq_to_mhz(tx_f_hz, scale='Hz')
            ch_row['Duplex'] = ch.duplex
            ch_row['Offset'] = format_freq_to_mhz(ch.offset_hz, scale='Hz')
            
            tx_sub = ch.tx_sub_audio_hz
            if tx_sub > 0:
                ch_row['Tone'] = 'Tone'
                ch_row['rToneFreq'] = format_sub_audio_to_hz(tx_sub, scale='Hz') / 1_000_000
            else:
                ch_row['rToneFreq'] = 0.0
            
            rx_sub = ch.rx_sub_audio_hz
            if rx_sub > 0:
                ch_row['cToneFreq'] = format_sub_audio_to_hz(rx_sub, scale='Hz') / 1_000_000
            else:
                ch_row['cToneFreq'] = 0.0

            
            ch_row['Mode'] = 'FM' if ch.rx_modulation == 'FM' else 'AM'
            ch_row['TStep'] = ch.bandwidth_hz / 1000
            ch_row['Power'] = format_power_to_chirp(ch.tx_power)
            
            ch_row.update({
                 'DtcsCode': '023',
                 'DtcsPolarity': 'NN',
                 'RxDtcsCode': '023',
                 'CrossMode': 'Tone->Tone',
                 'Skip': '1' if ch.skip else '0',
                 'Scan': '1' if ch.scan else '0',
                 'TalkAround': '1' if ch.talk_around else '0',
                 'Mute': '1' if ch.mute else '0',
                 'Sign': '1' if ch.sign else '0',
                 'TxDis': '1' if ch.tx_dis else '0',
                 'Bclo': '1' if ch.bclo else '0',
                 'PreDeEmphBypass': '1' if ch.pre_de_emph_bypass else '0',
                 'Comment': '',
                 'URCALL': '',
                 'RPT1CALL': '',
                 'RPT2CALL': '',
                 'DVCODE': ''
            })
            
            rows.append(ch_row)
            
        if not rows:
            return "", None
            
        output_df = pd.DataFrame(rows)
        chirp_cols = ['Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq', 'cToneF', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode', 'CrossMode', 'Mode', 'TStep', 'Skip', 'Power', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE', 'Scan', 'TalkAround', 'Mute', 'Sign', 'TxDis', 'Bclo', 'PreDeEmphBypass']
        
        # Correcting column names for output to match Chirp format expectations if necessary
        # But the columns are defined here.
        
        for col in chirp_cols:
            if col not in output_df.columns:
                output_df[col] = ''
        
        output_df = output_df[chirp_cols]
        if 'Location' not in output_df.columns:
            output_df.insert(0, 'Location', range(len(output_df)))
            
        return output_df.to_csv(index=False), None
