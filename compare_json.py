import json

def load_original(path):
    with open(path, 'r') as f:
        content = f.read()
        # Extract JSON part after 'BTECH UV'
        json_str = content.split('BTECH UV')[-1]
        return json.loads(json_str)

def load_roundtrip(path):
    with open(path, 'r') as f:
        return json.loads(f.read())

def compare():
    original_path = 'tests/data/example_clipboard_format.txt'
    roundtrip_path = 'tests/data/temp_clipboard_roundtrip.txt'
    
    original = load_original(original_path)
    roundtrip = load_roundtrip(roundtrip_path)

    if len(original['chs']) != len(roundtrip['chs']):
        print(f'Channel count mismatch: {len(original["chs"])} vs {len(roundtrip["chs"])}')
        return

    differences = 0
    for i, (orig_ch, rt_ch) in enumerate(zip(original['chs'], roundtrip['chs'])):
        if orig_ch != rt_ch:
            differences += 1
            print(f'Difference in channel {i}:')
            print(f'  Original: {orig_ch}')
            print(f'  Roundtrip: {rt_ch}')
    
    if differences == 0:
        print("No differences found in channels.")
    else:
        print(f"Found {differences} channels with differences.")

if __name__ == "__main__":
    compare()
