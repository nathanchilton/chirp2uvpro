import sys
import os

# Add src to sys.path so we can import the module
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src/converter'))

from converter.logic import btech_to_chirp

def test_json_with_prefix():
    content = 'BWE/BTECH JSON{"chs":[{"n":"Test","f":"146.520","d":"0","t":"None","dt":"None","s":"0","m":"FM"}]}'
    print(f"Testing content: {content}")
    output, error = btech_to_chirp(content)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Output:\n{output}")
    assert "Test" in output
    assert "146.52" in output

if __name__ == "__main__":
    try:
        test_json_with_prefix()
        print("JSON test passed!")
    except Exception as e:
        print(f"JSON test failed: {e}")
        sys.exit(1)
