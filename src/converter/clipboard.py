import json
import pandas as pd
import io
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator
from .utils import format_freq_to_hz, format_sub_audio_to_hz, normalize_power

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
                import json
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
        for header in ['title,', 'Name,']:
            idx = content.find(header)
            if idx != -1:
                content = content[idx:]
                break

        try:
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []
            return df.to_dict(orient='records')
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
            return json.dumps(channels, indent=2)
        elif self.format == 'csv':
            df = pd.DataFrame(channels)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
