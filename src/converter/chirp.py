import pandas as pd
import io
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator
from .utils import (
    format_freq_to_hz,
    format_sub_audio_to_hz,
    format_power_to_btech,
    format_power_to_chirp,
    normalize_power,
    is_true
)

class ChirpParser(BaseParser):
    def parse(self, content: str) -> List[Dict[str, Any]]:
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
            print(f"DEBUG: Columns found: {df.columns.tolist()}")
            if df.empty:
                return []
            
            channels = []
            for _, row in df.iterrows():
                ch = {}
                ch['name'] = str(next((row[k] for k in ['Name', 'title', 'name'] if k in row and pd.notna(row[k])), ''))
                
                tx_f_val = next((row[k] for k in ['Frequency', 'tx_freq', 'tx'] if k in row and pd.notna(row[k])), 0)
                tx_f = format_freq_to_hz(tx_f_val)
                
                rx_f_val = next((row[k] for k in ['rx_freq', 'rx_frequency', 'rx'] if k in row and pd.notna(row[k])), None)
                if rx_f_val is not None:
                    rx_f = format_freq_to_hz(rx_f_val)
                else:
                    duplex = str(row.get('Duplex', '-')).strip()
                    offset_val = row.get('Offset', 0)
                    offset_hz = format_freq_to_hz(offset_val)
                    if duplex == '-':
                        rx_f = tx_f - offset_hz
                    elif duplex == '+':
                        rx_f = tx_f + offset_hz
                    else:
                        rx_f = tx_f
                ch['tx_freq_hz'] = float(tx_f)
                ch['rx_freq_hz'] = float(rx_f)
                ch['offset_hz'] = offset_hz if 'offset_hz' in locals() else 0.0
                ch['duplex'] = duplex if 'duplex' in locals() else 'none'
                
                try:
                    bw_val = next((row[k] for k in ['TStep', 'bandwidth', 'bandwidth_hz'] if k in row and pd.notna(row[k])), 20.0)
                    ch['bandwidth_hz'] = int(float(bw_val) * 1000)
                except:
                    ch['bandwidth_hz'] = 25000
                
                tone_val = next((row[k] for k in ['Tone', 'CTCSS', 'DCS', 'tx_sub_audio(CTCSS=freq/DCS=number)', 'rx_sub_audio(CTCSS=freq/DCS=number)'] if k in row and pd.notna(row[k])), '')
                if str(tone_val).strip() != '':
                    r_tone = next((row[k] for k in ['rToneFreq', 'ctonef', 'ctcss', 'tx_sub_audio(CTCSS=freq/DCS=number)'] if k in row and pd.notna(row[k])), 0)
                    ch['tx_sub_audio_hz'] = format_sub_audio_to_hz(r_tone) if r_tone else 0.0
                    
                    rx_sub_val = next((row[k] for k in ['cToneF', 'rx_sub_audio', 'ctcss', 'rx_sub_audio(CTCSS=freq/DCS=number)'] if k in row and pd.notna(row[k])), None)
                    if rx_sub_val is not None and str(rx_sub_val).strip() != '':
                        ch['rx_sub_audio_hz'] = format_sub_audio_to_hz(rx_sub_val)
                    else:
                        ch['rx_sub_audio_hz'] = 0.0
                else:
                    ch['tx_sub_audio_hz'] = 0.0
                    ch['rx_sub_audio_hz'] = 0.0
                
                ch['tx_power'] = normalize_power(str(next((row[k] for k in ['Power', 'tx_power'] if k in row and pd.notna(row[k])), 'M')))
                
                # Handle flags
                for flag in ['scan', 'talk_around', 'pre_de_anch_bypass', 'sign', 'tx_dis', 'bclo', 'mute']:
                    col_name = None
                    for variant in [flag, flag.replace('_', '').capitalize(), flag.replace('_', ' ').title().replace(' ', ''), 'PreDeEmphBypass']:
                        if variant in df.columns:
                            col_name = variant
                            break
                    ch[flag] = is_true(row[col_name]) if col_name and col_name in row and pd.notna(row[col_name]) else False

                ch['rx_modulation'] = 'FM' if next((row[k] for k in ['Mode', 'rx_modulation', 'rx_mode'] if k in row and pd.notna(row[k])), 'FM') == 'FM' else 'AM'
                ch['tx_modulation'] = 'FM' if next((row[k] for k in ['Mode', 'tx_modulation', 'tx_mode'] if k in row and pd.notna(row[k])), 'FM') == 'FM' else 'AM'
                
                channels.append(ch)

            return channels
        except Exception as e:
            print(f"Error parsing Chirp CSV: {e}")
            return []

class ChirpGenerator(BaseGenerator):
    def generate(self, channels: List[Dict[str, Any]]) -> str:
        if not channels:
            return ""
            
        rows = []
        for ch in channels:
            ch_row = {}
            ch_row['Name'] = ch.get('name', '')
            
            tx_f_hz = ch.get('tx_freq_hz', 0)
            rx_f_hz = ch.get('rx_freq_hz', 0)
            ch_row['Frequency'] = tx_f_hz / 1_000_000
            
            if tx_f_hz < rx_f_hz:
                ch_row['Duplex'] = '+'
                ch_row['Offset'] = (rx_f_hz - tx_f_hz) / 1_000_000
            elif tx_f_hz > rx_f_hz:
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = (tx_f_hz - rx_f_hz) / 1_000_000
            else:
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = 0.0
                
            tx_sub = ch.get('tx_sub_audio_hz', 0)
            if tx_sub > 0:
                ch_row['Tone'] = 'Tone'
                ch_row['rToneFreq'] = tx_sub / 1_000_000 if tx_sub >= 1_000_000 else tx_sub
            else:
                ch_row['Tone'] = 'None'
                ch_row['rToneFreq'] = 0.0

            rx_sub = ch.get('rx_sub_audio_hz', 0)
            if rx_sub > 0:
                ch_row['cToneF'] = rx_sub / 1_000_000 if rx_sub >= 1_000_000 else rx_sub
            else:
                ch_row['cToneF'] = 0.0
                
            ch_row['Mode'] = 'FM' if ch.get('rx_modulation', 'FM') == 'FM' else 'NFM'
            ch_row['TStep'] = ch.get('bandwidth_hz', 25000) / 1000
            ch_row['Power'] = format_power_to_chirp(ch.get('tx_power', 'M'))
            
            ch_row.update({
                'DtcsCode': '023',
                'DtcsPolarity': 'NN',
                'RxDtcsCode': '023',
                'CrossMode': 'Tone->Tone',
                'Skip': '0' if ch.get('skip', False) else '1',
                'Scan': '1' if ch.get('scan', False) else '0',
                'TalkAround': '1' if ch.get('talk_around', False) else '0',
                'Mute': '1' if ch.get('mute', False) else '0',
                'Sign': '1' if ch.get('sign', False) else '0',
                'TxDis': '1' if ch.get('tx_dis', False) else '0',
                'Bclo': '1' if ch.get('bclo', False) else '0',
                'PreDeEmphBypass': '1' if ch.get('pre_de_emph_bypass', False) else '0',
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
        chirp_cols = ['Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq', 'cToneF', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode', 'CrossMode', 'Mode', 'TStep', 'skip', 'Power', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE', 'Scan', 'TalkAround', 'Mute', 'Sign', 'TxDis', 'Bclo', 'PreDeEmphBypass']
        
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
