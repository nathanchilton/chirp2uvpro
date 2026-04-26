import json
import pandas as pd
import io
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator
from .utils import format_freq_to_hz, format_sub_audio_to_hz, format_freq_to_mhz, format_sub_audio_to_mhz, normalize_power

class ClipboardParser(BaseParser):
    """
    Parser for Clipboard content (JSON or CSV).
    """
    def parse(self, content: str) -> List[Dict[str, Any]]:
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
                
                channels = []
                if isinstance(data, list):
                    channels = data
                elif isinstance(data, dict):
                    channels = data.get('chs', [])
                
                # Map abbreviated keys if they exist
                for ch in channels:
                    if 'n' in ch:
                        ch['name'] = ch.pop('n')
                    if 'rf' in ch:
                        ch['rx_freq_hz'] = format_freq_to_hz(ch.pop('rf'))
                    if 'tf' in ch:
                        ch['tx_freq_hz'] = format_freq_to_hz(ch.pop('tf'))
                    if 'ts' in ch:
                        ch['tx_sub_audio_hz'] = format_sub_audio_to_hz(ch.pop('ts'))
                    if 's' in ch:
                        ch['scan'] = str(ch.pop('s')) == '1'
                    if 'p' in ch:
                        ch['tx_power'] = normalize_power(ch.pop('p'))
                return channels
            except (json.JSONDecodeError, ValueError):
                pass

        # Try to find the start of CSV content
        for header in ['title,', 'Name,', 'name,']:
            idx = content.find(header)
            if idx != -1:
                content = content[idx:]
                break

        try:
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []
            
            channels = df.to_dict(orient='records')
            for ch in channels:
                for k, v in ch.items():
                    k_lower = k.lower()
                    if any(x in k_lower for x in ['rx_freq', 'tx_freq', 'rx_freq_hz', 'tx_freq_hz', 'rf', 'tf']):
                        ch[k] = format_freq_to_hz(v)
                    if any(x in k_lower for x in ['tx_sub_audio', 'tx_sub_audio_hz', 'ts', 'rx_sub_audio', 'rx_sub_audio_hz', 'rs']):
                        ch[k] = format_sub_audio_to_hz(v)
            return channels
        except Exception:
            return []

class ClipboardGenerator(BaseGenerator):
    """
    Generator for Clipboard content (JSON or CSV).
    """
    def __init__(self, format: str = 'json'):
        self.format = format.lower()

    def generate(self, channels: List[Dict[str, Any]]) -> str:
        if not channels:
            return ""

        channels = channels[:30]
            
        if self.format == 'json':
            abbreviated_channels = []
            for ch in channels:
                new_ch = {}
                if 'name' in ch: new_ch['n'] = ch['name']
                if 'rx_freq_hz' in ch: new_ch['rf'] = format_freq_to_mhz(ch['rx_freq_hz'])
                if 'tx_freq_hz' in ch: new_ch['tf'] = format_freq_to_mhz(ch['tx_freq_hz'])
                if 'tx_sub_audio_hz' in ch: new_ch['ts'] = ch['tx_sub_audio_hz']
                if 'scan' in ch: new_ch['s'] = 1 if ch['scan'] else 0
                if 'tx_power' in ch: new_ch['p'] = ch['tx_power']
                if 'id' in ch: new_ch['id'] = ch['id']
                # Copy other keys if they exist
                for k, v in ch.items():
                    if k not in ['name', 'rx_freq_fmt', 'tx_freq_hz', 'tx_sub_audio_hz', 'scan', 'tx_power', 'id', 'n', 'rf', 'tf', 'ts', 's', 'p']:
                        new_ch[k] = v
                abbreviated_channels.append(new_ch)
            return f"Copy this text and start BTECH UV{json.dumps({'chs': abbreviated_channels})}"
        elif self.format == 'csv':
            df = pd.DataFrame(channels)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
