import json
import pandas as pd
import io
from typing import List, Dict, Any

class ClipboardParser:
    def parse(self, content:str) -> List[Dict[str, Any]]:
        if not content or not content.strip():
            return []
        
        content = content.strip()
        print(f"DEBUG: content before stripping: {content}")

        # Strip known prefixes first so JSON parsing can work
        for prefix in ["BWE/BTECH JSON", "B1TECH UV", "BTECH UV"]:
            if content.startswith(prefix):
                content = content[len(prefix):].lstrip()
                print(f"DEBUG: content after stripping prefix: {content}")
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
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSONDecodeError: {e}")
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

parser = ClipboardParser()

print("--- Testing JSON with prefix ---")
json_with_prefix = 'BWE/BTECH JSON{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
print(f"Result: {parser.parse(json_with_prefix)}")

print("\n--- Testing JSON without prefix ---")
json_without_prefix = '{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
print(f"Result: {parser.parse(json_without_prefix)}")

print("\n--- Testing CSV with prefix ---")
csv_with_prefix = 'BTECH UVtitle,tx_freq,rx_freq\nTest,146520000,146520000'
print(f"Result: {parser.parse(csv_with_prefix)}")
