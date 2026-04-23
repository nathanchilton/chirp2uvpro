
from src.converter.logic import convert_format, ConversionError

def test_repro():
    csv_content = "column1,column2\nvalue1,value2"
    try:
        output_csv, warning = convert_format(csv_content, 'auto', 'btech')
        print(f"Success! Output: {output_csv}")
    except ConversionError as e:
        print(f"Caught ConversionError: {e}")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_repro()
