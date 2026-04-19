from src.converter.logic import chirp_to_btech
import io

def test_api_logic_simulation():
    # Simulate CSV content with > 30 channels
    # For this test, we'll just use the problematic file content
    csv_path = '../../tests/data/Yaesu_VX-6_20240203-Jacksonville.csv'
    try:
        with open(csv_path, 'r') as f:
            csv_content = f.read()
    except FileNotFoundError:
        print(f"Error: {csv_path} not found")
        return

    print(f"Simulating chirp_to_btech with {csv_path}")
    output_csv, warning = chirp_to_btech(csv_content)
    
    print(f"Output CSV length (chars): {len(output_csv)}")
    print(f"Warning: {warning}")
    
    if not output_csv:
        print("FAILURE: Simulation produced empty output_csv")
        return

    # Simulate the logic in upload_file
    if not output_csv:
        response_html = '<div class="alert alert-info mb-0">Conversion produced no content</div>'
        status_code = 200
    else:
        # Simulate warning_html generation
        warning_html = f'<div class="alert alert-warning mt-2 mb-0">{warning}</div>' if warning else ""
        response_html = f'''
        <div class="alert alert-success mb-0">
            uploaded and converted successfully!
            <div class="mt-2">
                <a href="/downloads/test.csv" class="btn btn-sm btn-success" download="test.csv">Download Converted File</a>
            </div>
        </div>
        {warning_html}
        '''
        status_code = 200
        
    print("Response HTML:")
    print(response_html)
    
    if "alert-warning" in response_html and "Truncated" in response_html:
        print("SUCCESS: Warning HTML correctly contains 'Truncated'")
    elif "alert-warning" not in response_html and warning:
        print("FAILURE: Warning HTML does not contain the warning")
    elif "alert-warning" in response_html and "Truncated" not in response_html:
        print("FAILURE: Warning HTML contains alert-warning but not the message 'Truncated'")
    else:
        print("FAILURE: Unexpected Response HTML structure")

if __name__ == "__main__":
    test_api_logic_simulation()
