import json
import pandas as pd
import io
from typing import List
from .base import BaseParser, BaseGenerator
from .models import Channel
from .utils import (
    format_freq_to_hz, 
    format_sub_audio_to_hz, 
    format_freq_to_mhz, 
    format_sub_audio_to_mhz, 
    normalize_power
)

class ClipboardParser(BaseParser):
    """
    Parser for Clipboard content (JSON or CSV).
    """
    def parse(self, content: str) -> List[Channel]:
        if not content or not content.strip():
            return []
        
        content = content.strip()

        # Try to find the start of JSON content
        json_start = -1
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
                    rx_freq_hz = format_freq_to_hz(ch_dict.get('rx_freq_hz', ch_dict.get('rf', 0)))
                    tx_freq_hz = format_freq_to_hz(ch_dict.get('tx_freq_hz', ch_dict.get('tf', 0)))
                    tx_sub_audio_hz = format_sub_audio_to_hz(ch_dict.get('tx_sub_audio_hz', ch_dict.get('ts', 0)))
                    rx_sub_audio_hz = format_sub_audio_to_hz(ch_dict.get('rx_sub_audio_hz', ch_dict.get('rs', 0)))
                    scan = str(ch_dict.get('scan', ch_dict.get('s', '0'))).strip() in ['1', 'true', 'True']
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
                'Copy this text and start BWE/BTECH JSON',
                'BTECH UV'
            ]
            for prefix in prefix_indicators:
                if content.startswith(prefix):
                    content = content[len(prefix):]
                    break
            
            df = pd.read_csv(io.StringIO(content))
            channels = []
            for _, row in df.iterrows():
                name = str(row.get('name', ''))
                rx_freq_hz = format_freq_to_hz(row.get('rx_freq_hz', 0))
                tx_freq_hz = format_freq_to_hz(row.get('tx_freq_hz', 0))
                tx_sub_audio_hz = format_sub_audio_to_hz(row.get('tx_sub_audio_hz', 0))
                rx_sub_audio_hz = format_sub_audio_to_hz(row.get('rx_sub_audio_hz', 0))
                scan = str(row.get('scan', '0')).strip() in ['1', 'true', 'True']
                tx_power = normalize_power(row.get('tx_power', 'M'))

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
                    "rf": format_freq_to_mhz(ch.rx_freq_hz),
                    "tf": format_freq_to_mhz(ch.tx_freq_hz),
                     "ts": ch.tx_sub_audio_hz,
                     "rs": ch.rx_sub_audio_hz,
                     "s": 1 if ch.scan else 0,
                    "id": 0, # Dummy
                    "p": "0" # Dummy
                })
            
            data = {"chs": chs}
            return f'Copy this text and start BTECH UV{json.dumps(data)}', status_msg
        
        elif self.format == 'csv':
            if not channels:
                return "", None
            # Generate CSV format
            output = "Copy this text and start BTECH UVname,tx_freq_hz,rx_freq_hz,tx_sub_audio_hz,rx_sub_audio_hz\n"
            for ch in channels:
                 output += f"{ch.name},{format_freq_to_mhz(ch.tx_freq_hz)},{format_freq_to_mhz(ch.rx_freq_hz)},{ch.tx_sub_audio_hz},{ch.rx_sub_audio_hz}\n"
            return output.strip(), status_msg
        
        return "", None
