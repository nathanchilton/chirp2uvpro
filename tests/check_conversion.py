from converter.logic import convert_format

def test_conversion_chirp_to_btech():
    chirp_content = "Channel,Name,Frequency,Duplex,Tone,Dtune,Skip,Mode\n1,Test,146.520,0,None,None,0,FM\n2,Test2,146.550,0,None,None,0,FM"
    output_csv, warning = convert_format(chirp_content, 'auto', 'btech')
    # Check if certain key information is present in the output
    assert "Test" in output_csv
    assert "146.52" in output_csv
    assert "146.55" in output_csv
    assert "FM" in output_csv

def test_conversion_btech_to_chirp():
    btech_content = 'BTECH UV{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"},{"n":"Test2","f":"146.550","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
    output_csv, warning = convert_format(btech_content, 'btech', 'chirp')
    # Check if certain key information is present in the output
    assert "Test" in output_csv
    assert "146.52" in output_csv
    assert "146.55" in output_csv
    assert "FM" in output_csv
