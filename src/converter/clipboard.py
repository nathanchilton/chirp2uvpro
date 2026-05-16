import json
import pandas as pd
import io
from typing import List
from .base import BaseParser, BaseGenerator
from .models import Channel
from .utils import (
    format_freq_to_hz, 
    format_sub_audio_to_hz, 
    format_sub_audio_to_units,
    format_freq_to_mhz, 
    normalize_power
)

class ClipboardParser(BaseParser):
    """
    Parser for Clipboard content (JSON or CSV).
    """
    def parse(self, content: str | tuple[str, str | None]) -> List[Channel]:
        if isinstance(content, tuple):
            content = content[0]
        if not content or not content.strip():
            return []
        
        content = content.strip()
        
        # Try to find the start of JSON content
        json_start = -1
        prefix = "Copy this text and start BTECH UV"
        if content.startswith(prefix):
            for char in ['{', '[']:
                idx = content.find(char, len(prefix))
                if idx != -1:
                    if json_start == -1 or idx < json_start:
                        json_start = idx
        else:
            # Support partial prefix like "BTECH UV"
            for p in ["BTECH UV", ""]:
                if p and content.startswith(prefix + p):
                    # This is a bit complex, let's just check if it starts with a known prefix
                    pass
            for char in ['{', '[']:
                idx = content.find(char)
                if idx != -1:
                    if json_start == -1 or idx < json_start:
                        json_start = idx
        
        if json_start != -1:
            try:
                json_content = content[json_start:]
                data = json.loads(json_content)
                
                channels_data = []
                if isinstance(data, list):
                    channels_data = data
                elif isinstance(data, dict):
                    channels_data = data.get('chs', [])
                
                channels = []
                for ch in channels_data:
                    if not isinstance(ch, dict):
                        continue
                    
                    ch_dict = ch.copy()
                    
                    name = ch_dict.get('name', ch_dict.get('n', ''))
                    # JSON format uses MHz for frequencies
                    rx_freq_hz = format_freq_to_hz(ch_dict.get('rx_freq_hz', ch_dict.get('rf', 0)), scale='MHz')
                    tx_freq_hz = format_freq_to_hz(ch_dict.get('tx_freq_hz', ch_dict.get('tf', 0)), scale='MHz')
                    # JSON format uses 0.01Hz units for sub-audio
                    # We must handle the case where sub-audio is CTCSS (Hz * 100) vs DCS (Hz)
                    # If the value is high (e.g., > 2000), it's likely CTCSS frequency * 100
                    tx_sub_raw = ch_dict.get('tx_sub_audio_hz', ch_dict.get('ts', 0))
                    rx_sub_raw = ch_dict.get('rx_sub_audio_hz', ch_dict.get('rs', 0))
                    
                    def parse_sub_audio(val):
                        # If it's a number, check if it looks like CTCSS (scaled by 100)
                        try:
                            f_val = float(val)
                            if f_val > 1000: # Heuristic: CTCSS tones are < 2000Hz, but scaled by 100
                                return format_sub_audio_to_hz(f_val, scale='0.01Hz')
                            return format_sub_audio_to_hz(f_val, scale='Hz')
                        except:
                            return 0.0

                    tx_sub_audio_hz = parse_sub_audio(tx_sub_raw)
                    rx_sub_audio_hz = parse_sub_audio(rx_sub_raw)
                    
                    scan_val = str(ch_dict.get('scan', ch_dict.get('s', '0')))
                    
                    scan = scan_val.strip() in ['1', 'format', 'true', 'True', 'trans']
                    
                    tx_power = normalize_power(ch_dict.get('tx_power', ch_dict.get('p', 'M')))
                    
                    channels.append(Channel(
                        name=name,
                        rx_freq_hz=rx_freq_hz,
                        tx_freq_hz=tx_freq_hz,
                        tx_sub_audio_hz=tx_sub_audio_hz,
                        rx_sub_audio_hz=rx_sub_audio_hz,
                        scan=scan,
                        tx_power=tx_power
                    ))
                return channels
            
            except (json.JSONDecodeError, ValueError, KeyError):
                pass
        
        # If not JSON, try CSV
        try:
            prefix_indicators = [
                'Copy this text and start BTECH UV',
                'BTECH UV'
            ]
            freq_scale = 'MHz' # Default for CSV if not specified
            for prefix in prefix_indicators:
                if content.startswith(prefix):
                    content = content[len(prefix):].lstrip()
                    freq_scale = 'Hz' # BTECH format uses Hz if it has the prefix
                    break
            
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []

            cols = df.columns.tolist()
            def find_col(keywords):
                for kw in keywords:
                    for col in cols:
                        if kw.lower() in col.lower():
                            return col
                return None

            col_map = {
                'name': find_col(['title', 'name', 'channel']),
                'rx_freq': find_col(['rx_freq', 'frequency', 'rx']),
                'tx_freq': find_col(['tx_freq', 'frequency', 'tx']),
                'tx_sub_audio': find_col(['tx_sub_audio', 'ctcss', 'dcs', 'rToneFreq']),
                'rx_sub_audio': find_col(['rx_sub_audio', 'ctcss', 'dcs', 'cToneF', 'cToneFreq']),
                'tx_power': find_col(['tx_power', 'pad', 'power']),
                'scan': find_col(['scan']),
            }

            channels = []
            for _, row in df.iterrows():
                name = str(row[col_map['name']]) if col_map['name'] and not pd.isna(row[col_map['name']]) else ''
                
                tx_f_val_raw = row[col_map['tx_freq']] if col_map['tx_freq'] and not pd.isna(row[col_map['tx_freq']]) else 0.0
                rx_f_val_raw = row[col_map['rx_freq']] if col_map['rx_freq'] and not pd.isna(row[col_map['rx_freq']]) else 0.0
                tx_f_hz = format_freq_to_hz(tx_f_val_raw, scale=freq_scale)
                rx_f_hz = format_freq_to_hz(rx_f_val_raw, scale=freq_scale)

                tx_sub_val_raw = row[col_map['tx_sub_audio']] if col_map['tx_sub_audio'] and not pd.isna(row[col_map['tx_sub_audio']]) else 0.0
                rx_sub_val_raw = row[col_map['rx_sub_audio']] if col_map['rx_sub_audio'] and not pd.isna(row[col_map['rx_sub_audio']]) else 0.0
                
                def parse_sub_audio_csv(val):
                    try:
                        f_val = float(val)
                        if f_val > 1000: # Heuristic: CTCSS tones are < 2000Hz, but scaled by 100
                            return format_sub_audio_to_hz(f_val, scale='0.01Hz')
                        return format_sub_audio_to_hz(f_val, scale='Hz')
                    except:
                        return 0.0

                tx_sub_hz = parse_sub_audio_csv(tx_sub_val_raw)
                rx_sub_hz = parse_sub_audio_csv(rx_sub_val_raw)

                scan_val = str(row[col_map['scan']]) if col_map['scan'] and not pd.isna(row[col_map['scan']]) else '0'
                scan = scan_val.strip() in ['1', 'true', 'True']

                tx_power = normalize_power(row[col_map['tx_power']]) if col_map['tx_power'] and not pd.isna(row[col_map['tx_power']]) else 'M'
                
                channels.append(Channel(
                    name=name,
                    rx_freq_hz=rx_f_hz,
                    tx_freq_hz=tx_f_hz,
                    tx_sub_audio_hz=tx_sub_hz,
                    rx_sub_audio_hz=rx_sub_hz,
                    scan=scan,
                    tx_power=tx_power
                ))
            return channels
        except Exception:
            pass
        
        return []

class ClipboardGenerator(BaseGenerator):
    """
    Generator for Clipboard content (JSON).
    """
    def __init__(self, format: str = 'json'):
        self.format = format
    
    def generate(self, channels: List[Channel]) -> tuple[str, str | None]:
        status_msg = None
        if len(channels) > 30:
            channels = channels[:30]
            status_msg = "Truncated"
        
        if self.format == 'json':
            chs = []
            for ch in channels:
                chs.append({
                                    "n": ch.name,
                                    "rf": format_freq_to_mhz(ch.rx_freq_hz, scale='Hz'),
                                    "tf": format_freq_to_mhz(ch.tx_freq_hz, scale='Hz'),
                                    "ts": format_sub_audio_to_units(ch.tx_sub_audio_hz, unit_scale='0.01Hz'),
                                    "rs": format_sub_audio_to_units(ch.rx_sub_audio_hz, unit_scale='0.01Hz'),
                                    "s": 1 if ch.scan else 0,
                                    "id": 0, # Dummy
                                    "p": ch.tx_power.replace('W', '') if 'W' in ch.tx_power else ch.tx_power
                                })
            
            data = {"chs": chs}
            # Use the required prefix for BTECH UV parsing
            return f'Copy this text and start BTECH UV{json.dumps(data)}', status_msg
        
        elif self.format == 'csv':
            if not channels:
                return "", None
            # Generate CSV format
            output = "Copy this text and start BTECH UVname,tx_freq_hz,rx_freq_hz,tx_sub_audio_hz,rx_sub_audio_hz\n"
            for ch in channels:
                output += f"{ch.name},{format_freq_to_hz(ch.tx_freq_hz, scale='Hz')},{format_freq_to_hz(ch.rx_freq_hz, scale='Hz')},{ch.tx_sub_audio_hz},{ch.rx_sub_audio_hz}\n"
            return output.strip(), status_msg
        
        return "", None
