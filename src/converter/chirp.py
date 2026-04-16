import pandas as pd
import io
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator
from .utils import (
    format_freq_to_hz,
    format_sub_audio_to_hz,
    format_power_to_btech,
    format_power_to_chirp,
    normalize_power
)

class ChirpParser(BaseParser):
    def parse(self, content: str) -> List[Dict[str, Any]]:
        if not content:
            return []
        
        # Strip known prefixes
        prefixes = ["BWE/BTECH JSON", "BWE/BTECH CSV", "B1TECH UV", "BTECH UV"]
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
                ch['name'] = str(row.get('Name', ''))
                
                tx_f_val = row.get('Frequency', 0)
                tx_f = format_freq_to_hz(tx_f_val)
                
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
                
                try:
                    ch['bandwidth_hz'] = int(float(row.get('TStep', 25.0) * 1000))
                except:
                    ch['bandwidth_hz'] = 25000
                
                tone = str(row.get('Tone', ''))
                if tone in ['Tone', 'CTCSS']:
                    r_tone = float(row.get('rToneFreq', 0))
                    ch['tx_sub_audio_hz'] = format_freq_to_hz(r_tone)
                    ch['rx_sub_audio_hz'] = format_freq_to_hz(r_tone)
                else:
                    ch['tx_sub_audio_hz'] = 0.0
                    ch['rx_sub_audio_hz'] = 0.0
                
                ch['tx_power'] = normalize_power(str(row.get('Power', '')))
                ch['scan'] = False
                ch['talk_around'] = False
                ch['pre_de_emph_bypass'] = False
                ch['sign'] = False
                ch['tx_dis'] = False
                ch['bclo'] = False
                ch['mute'] = False
                ch['rx_modulation'] = 'FM' if row.get('Mode', 'FM') == 'FM' else 'AM'
                ch['tx_modulation'] = 'FM' if row.get('Mode', 'FM') == 'FM' else 'AM'
                
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
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = (rx_f_hz - tx_f_hz) / 1_000_000
            elif tx_f_hz > rx_f_hz:
                ch_row['Duplex'] = '+'
                ch_row['Offset'] = (tx_f_hz - rx_f_hz) / 1_000_000
            else:
                ch_row['Duplex'] = '-'
                ch_row['Offset'] = 0.0
                
            tx_sub = ch.get('tx_sub_audio_hz', 0)
            if tx_sub > 0:
                ch_row['Tone'] = 'Tone'
                ch_row['rToneFreq'] = tx_sub / 1_000_000
            else:
                ch_row['Tone'] = 'None'
                ch_row['rToneFreq'] = 0.0
                
            ch_row['Mode'] = 'FM' if ch.get('rx_modulation', 'FM') == 'FM' else 'NFM'
            ch_row['TStep'] = ch.get('bandwidth_hz', 25000) / 1000
            ch_row['Power'] = format_power_to_chirp(ch.get('tx_power', 'M'))
            
            ch_row.update({
                'DtcsCode': '023',
                'DtcsPolarity': 'NN',
                'RxDtcsCode': '023',
                'CrossMode': 'Tone->Tone',
                'Skip': '0',
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
        chirp_cols = ['Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq', 'cToneF', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode', 'CrossMode', 'Mode', 'TStep', 'Skip', 'Power', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE']
        
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
