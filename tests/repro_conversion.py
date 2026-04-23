from converter.logic import convert_format

def test_conversions():
    content = "channel,frequency,mode\n1,144.000,FM\n2,145.000,FM"
    
    print("--- Testing CHIRP to BTECH ---")
    out, warn = convert_format(content, 'chirp', 'btech')
    print(f"Output:\n{out}")
    print(f"Warning: {warn}")

    print("\n--- Testing BTECH to CHIRP ---")
    out, warn = convert_format(content, 'btech', 'chirp')
    print(f"Output:\n{out}")
    print(f"Warning: {warn}")

    print("\n--- Testing BTECH to CLIPBOARD ---")
    out, warn = convert_format(content, 'btech', 'clipboard')
    print(f"Output:\n{out}")
    print(f"Warning: {warn}")

if __name__ == "__main__":
    test_conversions()
