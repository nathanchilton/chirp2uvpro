import pandas as pd
import io
from typing import List
from .base import BaseParser, BaseGenerator
from .models import Channel
from .utils import (
    format_freq_to_hz,
    format_sub_audio_to_hz,
    format_power_to_btech,
    format_power_to_chirp,
    normalize_power,
    is_true
)

class ChirpParser(BaseParser):
    def parse(self, content: str) -> List[Channel]:
        if not content:
            return []
        
        # Strip known prefixes
        prefixes = ["BWE/BCR JSON", "BWE/BTECH CSV", "B1TECH UV", "BTECH UV"]
        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].lstrip()
                break
        
        try:
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []
            
            channels = []
            for _, row in df.iterrows():
                ch = Channel()
                ch.name = str(next((row[k] for k in ['Name', 'title', 'name'] if k in row and pd.notna(row[k])), ''))
                ch.location = str(next((row[k] for k in ['Location', 'location', 'loc'] if k in row and pd.notna(row[k])), ''))
                
                tx_f_val = next((row[k] for k in ['Frequency', 'tx_freq', 'tx'] if k in row and pd.notna(row[k])), 0)
                ch.tx_freq_hz = float(format_freq_to_hz(tx_f_val))
                
                rx_f_val = next((row[k] for k in ['rx_freq', 'rx_frequency', 'rx'] if k in row and pd.notna(row[k])), None)
                duplex = 'none'
                offset_hz = 0.0
                
                # Always try to get duplex and offset if they exist
                duplex_val = row.get('Duplex', None)
                if pd.notna(duplex_val):
                    duplex = str(duplex_val).strip()
                
                offset_val = row.get('Offset', 0)
                if pd.notna(offset_val):
                    offset_hz = float(format_freq_to_hz(offset_val))
                
                if rx_f_val is not None:
                    ch.rx_freq_hz = float(format_freq_to_hz(rx_f_val))
                else:
                    if duplex == '-':
                        ch.rx_freq_hz = ch.tx_freq_hz - offset_hz
                    elif duplex == '+':
                        ch.rx_freq_hz = ch.tx_freq_hz + offset_hz
                    else:
                        ch.rx_freq_hz = ch.tx_freq_hz
                
                ch.offset_hz = offset_hz
                ch.duplex = duplex
                
                try:
                    bw_val = next((row[k] for k in ['TStep', 'bandwidth', 'bandwidth_hz', 'bandwidth(12500/25000)'] if k in row and pd.notna(row[k])), 25000.0)
                    if bw_val < 3000: # Assumes kHz
                        ch.bandwidth_hz = int(float(bw_val) * 1000)
                    else: # Assumes Hz
                        ch.bandwidth_hz = int(float(bw_val))
                except:
                    ch.bandwidth_hz = 25000
                
                # Parse TX sub-audio frequency independently
                r_tone = next((row[k] for k in ['rToneFreq', 'ctonef', 'ctost', 'tx_sub_audio', 'rx_sub_audio', 'tx_sub_audio(CTCSS=freq/DCS=number)', 'rx_sub_audio(CTCSS=forDCS=number)'] if k in row and pd.notna(row[k])), 0)
                ch.tx_sub_audio_hz = float(format_sub_audio_to_hz(r_tone)) if r_tone else 0.0

                # Parse RX sub-audio frequency independently
                rx_sub_val = next((row[k] for k in ['cToneF', 'cToneFreq', 'rx_sub_audio', 'ctcss', 'tx_sub_audio', 'rx_sub_audio(CTCSS=freq/DCS=number)', 'tx_sub_audio(CTCSS=freq/DCS=number)'] if k in row and pd.notna(row[k])), 0)
                ch.rx_sub_audio_hz = float(format_sub_audio_to_hz(rx_sub_val)) if rx_sub_val else 0.0

                
                tx_p_val = next((row[k] for k in ['Power', 'tx_perm', 'p'] if k in row and pd.notna(row[k])), 'M')
                ch.tx_power = tx_p_val

                ch.skip = is_true(next((row[k] for k in ['Skip', 'skip'] if k in row and pd.notna(row[k])), False))

                # Handle flags
                for flag in ['scan', 'talk_around', 'pre_de_emph_bypass', 'sign', 'tx_dis', 'bclo', 'mute']:
                    col_name = None
                    for variant in [flag, flag.replace('_', '').capitalize(), flag.replace('_', ' ').title().replace(' ', ''), 'PreDeEmphBypass']:
                        if variant in df.columns:
                            col_name = variant
                            break
                    if col_name and col_name in row and pd.notna(row[col_name]):
                        setattr(ch, flag, is_true(row[col_name]))
                    else:
                        setattr(ch, flag, False)

                ch.rx_modulation = 'FM' if next((row[k] for k in ['Mode', 'rx_modulation', 'rx_mode'] if k in row and pd.notna(row[k])), 'FM') == 'F' or next((row[k] for k in ['Mode', 'rx_modulation', 'rx_mode'] if k in row and pd.notna(row[k])), 'FM') == 'FM' else 'AM'
                
                channels.append(ch)
            
            return channels
        except Exception as e:
            print(f"Error parsing Chirp CSV: {e}")
            return []

class ChirpGenerator(BaseGenerator):
    def generate(self, channels: List[Channel]) -> str:
        if not channels:
            return ""
            
        rows = []
        for ch in channels:
            ch_row = {}
            ch_rel_name = ch.name
            ch_row['Name'] = ch_rel_name
            ch_row['Location'] = ch.location
            
            tx_f_hz = ch.tx_freq_hz
            rx_f_hz = ch.rx_freq_hz
            ch_row['Frequency'] = tx_f_hz / 1_000_000
            
            if tx_f_hz < rx_f_hz:
                ch_row['Duplex'] = '+'
                ch_row['Offset'] = (rx_f_hz - tx_f_hz) / 1_000_000
            elif tx_f_hz > rx_f_hz:
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = (tx_f_hz - rx_f_hz) / 1_000_000
            else:
                ch_row['Duplex'] = 'none'
                ch_row['Offset'] = 0.0
                
            tx_sub = ch.tx_sub_audio_hz
            if tx_sub > 0:
                ch_row['Tone'] = 'Tone'
                ch_row['rToneFreq'] = tx_sub
            else:
                ch_row['Tone'] = 'None'
                ch_row['rToneFreq'] = 0.0

            rx_sub = ch.rx_sub_audio_hz
            if rx_sub > 0:
                ch_row['cToneF'] = rx_sub
            else:
                ch_row['cToneF'] = 0.0
            
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
            return ""
            
        output_df = pd.DataFrame(rows)
        chirp_cols = ['Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq', 'cToneF', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode', 'CrossMode', 'Mode', 'TStep', 'Skip', 'Power', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE', 'Scan', 'TalkAround', 'Mute', 'Sign', 'TxDis', 'Bclo', 'PreDeEmphBypass']
        
        for col in chirp_cols:
            if col not in output_df.columns:
                output_df[col] = ''
        
        output_df = output_df[chirp_cols]
        if 'Location' not in output_df.columns:
            output_df.insert(0, 'Location', range(len(output_df)))
            
        def format_freq_for_chirp(f_val):
            try:
                f = float(f_val)
                if f >= 1_000_000:
                    return f / 1_000_000
                return f
            except:
                return 0.0
                
        output_df['Frequency'] = output_df['Frequency'].apply(format_freq_for_chirp)
        
        return output_df.to_csv(index=False)

