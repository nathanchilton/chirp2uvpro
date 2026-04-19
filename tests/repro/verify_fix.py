import pandas as pd
import io
from src.converter.logic import chirp_to_btech

def test_truncation():
    csv_path = '../../tests/data/Yaesu_VX-6_20240203-Jacksonville.csv'
    print(f"Testing with {csv_path}")
    
    try:
        with open(csv_path, 'r') as f:
            csv_content = f.read()
    except FileNotFoundError:
        print(f"Error: {csv_path} not found")
        return

    output_csv, status_msg = chirp_to_btech(csv_content)
    
    if not output_csv:
        print("FAILURE: Conversion produced empty content")
        return

    print(f"Status Message: {status_msg}")
    
    # Check number of lines in output. 
    # The header is 1 line, then 30 rows of channels.
    lines = output_csv.strip().split('\n')
    num_channels = len(lines) - 1
    print(f"Number of channels in output: {num_channels}")
    
    if num_channels > 30:
        print("FAILURE: More than 30 channels in output")
    elif num_channels <= 30 and status_msg == "Truncated":
        print("SUCCESS: Truncation worked correctly and status message is 'Truncated'")
    elif num_channels <= 30 and status_msg is None:
        print("FAILURE: Status message is not 'Truncated'")
    else:
        print(f"FAILURE: Unexpected result. Status: {status_msg}, Channels: {num_channels}")

if __name__ == "__main__":
    test_truncation()
