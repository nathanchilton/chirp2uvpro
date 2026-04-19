import io
import pandas as pd
import re

def btech_to_chirp_fixed(csv_content: str):
    try:
        # Try to find the start of the CSV content
        # We look for common headers or just a comma
        match = re.search(r'(title,|Name,)', csv_content, re.DOTALL)
        if match:
            csv_content = match.group(1) + csv_content[match.start(1)+len(match.group(1).split(',')[0]):] # This is a bit complex
            # Simpler:
            idx = csv_content.find('title,')
            if idx != -1:
                csv_content = csv_content[idx:]
            else:
                idx = csv_content.find('Name,')
                if idx != -1:
                    csv_content = csv_content[idx:]
        
        # Actually, let's just use a simpler approach: find the first comma that is followed by something
        # Or just strip common prefixes.
        
        # Let's try stripping common prefixes
        for prefix in ["BWE/BTECH JSON", "BTECH UV"]:
            if csv_content.startswith(prefix):
                csv_content = csv_content[len(prefix):]
                break

        print(f"DEBUG: csv_content: {csv_content}")
        df = pd.read_csv(io.StringIO(csv_content))
        print(f"DEBUG: df:\n{df}")
        if df.empty:
            return "", None
        return df.to_csv(index=False), None
    except Exception as e:
        return "", str(e)

def btech_to_chirp_unfixed(csv_content: str):
    try:
        print(f"DEBUG: csv_content: {csv_content}")
        df = pd.read_csv(io.StringIO(csv_content))
        print(f"DEBUG: df:\n{df}")
        if df.empty:
            return "", None
        return df.to_csv(index=False), None
    except Exception as e:
        return "", str(e)

# Test case 1: JSON-like content (with prefix)
btech_content_json = 'BWE/BTECH JSON{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
print("\n--- Testing JSON-like content ---")
output, error = btech_to_chirp_unfixed(btech_content_json)
print(f"Output: {output}")
print(f"Error: {error}")

output_fixed, error_fixed = btech_to_chirp_fixed(btech_content_json)
print(f"Fixed Output: {output_fixed}")
print(f"Fixed Error: {error_fixed}")

# Test case 2: CSV with prefix
csv_header = "title,tx_freq,rx_freq,tx_sub_audio(CTCSS=freq/DCS=number),rx_sub_audio(CTCSS=freq/DCS=number),tx_power(H/M/L),bandwidth(12500/25000),scan(0=OFF/1=ON),talk around(0=OFF/1=ON),pre_de_emph_bypass(0=OFF/1=ON),sign(0=OFF/1=ON),tx_dis(0=OFF/1=ON),bclo(0=OFF/1=ON),mute(0=OFF/1=ON),rx_modulation(0=FM/1=AM),tx_modulation(0=FM/1=AM)"
csv_row = "Test,146520000,146520000,0,0,M,25000,0,0,0,0,0,0,0,FM,FM"
btech_content_csv = 'BTECH UV' + csv_header + '\n' + csv_row

print("\n--- Testing CSV with prefix ---")
output, error = btech_to_chirp_unfixed(btech_content_csv)
print(f"Output: {output}")
print(f"Error: {error}")

output_fixed, error_fixed = btech_to_chirp_fixed(btech_content_csv)
print(f"Fixed Output: {output_fixed}")
print(f"Fixed Error: {error_fixed}")
