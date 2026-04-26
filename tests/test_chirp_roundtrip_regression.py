import pytest
import pandas as pd
import os
from src.converter.btech import BtechParser, BtechGenerator
from src.converter.chirp import ChirpParser, ChirpGenerator

def test_chirp_roundtrip_with_example_file():
    original_file = 'tests/data/example_chirp_format.csv'
    btech_output = 'tests/data/output_btech.csv'
    chirp_back_output = 'tests/data/output_chirp_back.csv'
    
    assert os.path.exists(original_file)
    
    # 1. CHIRP -> BTECH
    chirp_parser = ChirpParser()
    btech_gen = BtechGenerator()
    
    with open(original_file, 'r') as f:
        chirp_content = f.read()
    
    btech_content = btech_gen.generate(chirp_parser.parse(chirp_content))
    with open(btech_output, 'w') as f:
        f.write(btech_content)
    
    # 2. BTECH -> CHIRP
    btech_parser = BtechParser()
    chirp_gen = ChirpGenerator()
    
    with open(btech_output, 'r') as f:
        btech_content_read = f.read()
        
    chirp_back_content = chirp_gen.generate(btech_parser.parse(btech_content_read))
    with open(chirp_back_output, 'w') as f:
        f.write(chirp_back_content)
    
    # 3. Verify
    original_df = pd.read_csv(original_file)
    back_df = pd.read_csv(chirp_back_output)
    
    # We check the first 30 channels.
    # The original file has 198 lines. Let's take the first 30.
    original_subset = original_df.head(30).copy()
    back_subset = back_df.head(30).copy()
    
    # Check that the number of rows matches (or at least we can compare)
    # Since BTECH only keeps 30 channels, back_df might only have 30.
    
    # Check columns that should be present and identical
    # We know cToneFreq -> cToneF was a change, so we'll check the ones that should match
    # For now, let's just check if the number of rows is at least 30
    assert len(back_subset) >= 30
    
    # Check that the names are the same
    assert (original_subset['Name'] == back_subset['Name']).all()
    
    # Check that the frequencies are the same (within precision)
    pd.testing.assert_series_equal(original_subset['Frequency'], back_subset['Frequency'], check_dtype=False)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
