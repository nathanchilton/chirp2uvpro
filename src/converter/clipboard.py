import json
import pandas as pd
import io
from typing import List, Dict, Any
from .base import BaseParser, BaseGenerator

class ClipboardParser(BaseParser):
    """
    Parser for Clipboard content (JSON or CSV).
    """
    def parse(self, content: str) -> List[Dict[str, Any]]:
        if not content or not content.strip():
            return []
        
        content = content.strip()

        # Strip known prefixes first so JSON parsing can work
        for prefix in ["BWE/BTECH JSON", "B1TECH UV", "BTECH UV"]:
            if content.startswith(prefix):
                content = content[len(prefix):].lstrip()
                break
        
        # Try JSON first
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                return []
        except json.JSONDecodeError:
            pass
            
        # Try CSV
        try:
            df = pd.read_csv(io.StringIO(content))
            if df.empty:
                return []
            return df.to_dict(orient='records')
        except Exception as e:
            print(f"Error parsing clipboard content: {e}")
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
            
        if self.format == 'json':
            return json.dumps(channels, indent=2)
        elif self.format == 'csv':
            df = pd.DataFrame(channels)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
