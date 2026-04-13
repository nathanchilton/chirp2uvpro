import os
import sqlite3
import uuid
from flask import Blueprint, request, jsonify, render_template
from converter.logic import chirp_to_btech, btech_to_chirp, clipboard_to_internal_wrapper, internal_to_clipboard, ConversionError
from database import get_db_connection

api_bp = Blueprint('api', __name__)
# Use absolute path or relative to app root for consistency
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_bp.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200

@api_bp.route('/convert/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '<div class="alert alert-danger mb-0">No file part</div>', 400
    file = request.files['file']
    if file.filename == '':
        return '<div class' + '="alert alert-danger mb-0">No selected file</div>', 400
    
    try:
        # Determine direction based on filename or presence of specific string
        # For simplicity, we'll assume if it contains 'btech', it's btech_to_chirp
        # Otherwise, it's chirp_to_btech
        direction = 'btech_to_chirp' if 'btech' in file.filename.lower() else 'chirp_to_btech'
        
        filename = str(uuid.uuid4()) + "_" + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Read content for conversion
        with open(file_path, 'r') as f:
            csv_content = f.read()
        
        if direction == 'chirp_to_btech':
            output_csv, warning = chirp_to_btech(csv_content)
        elif direction == 'btech_to_chirp':
            output_csv, warning = btech_to_chirp(csv_content)
        elif direction == 'clipboard_to_internal':
            internal_channels, warning = clipboard_to_internal_wrapper(csv_content)
            output_csv = internal_to_clipboard(internal_channels)
        else:
            return '<div class="alert alert-danger mb-0">Invalid direction</div>', 400
        
        if not output_csv:
            return '<div class="alert alert-info mb-0">Conversion produced no content</div>', 200
        
        # Create output filename
        output_filename = f"converted_{uuid.uuid4()}.csv"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, 'w') as f:
            f.write(output_csv)
            
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT INTO conversion_history (input_filename, output_filename, status, warning) VALUES (?, ?, ?, ?)',
                (filename, output_filename, 'success', warning)
            )
        
        download_url = f"/downloads/{output_filename}"
        warning_html = f'<div class="alert alert-warning mt-2 mb-0">{warning}</div>' if warning else ""
        
        return f'''
        <div class="alert alert-success mb-0">
            uploaded and converted successfully!
            <div class="mt-2">
                <a href="{download_url}" class="btn btn-sm btn-success" download="{output_filename}">Download Converted File</a>
            </div>
        </div>
        {warning_html}
        ''', 200
        
    except ConversionError as e:
        return f'<div class="alert alert-danger mb-0">Conversion Error: {str(e)}</div>', 400
    except Exception as e:
        import traceback
        print(f"Error in upload_file: {str(e)}")
        traceback.print_exc()
        return f'<div class="alert alert-danger mb-0">Error: {str(e)}</div>', 500

@api_bp.route('/convert/paste', methods=['POST'])
def convert_paste():
    try:
        data = request.get_json(silent=True)
        if data is None:
            data = request.form
        
        print(f"DEBUG: convert_paste data: {dict(data) if hasattr(data, 'items') else data}")
            
        content = data.get('content') or data.get('csv_content')
        if not content:
            print("DEBUG: convert_paste - No content provided")
            return '<div class="alert alert-danger mb-0">No content provided</div>', 400
        
        csv_content = content
        direction = data.get('direction', 'chirp_to_btech')
        print(f"DEBUG: convert_paste - direction: {direction}")
        
        if direction == 'chirp_to_btech':
            output_csv, warning = chirp_to_btech(csv_content)
        elif direction == 'btech_to_chirp':
            output_csv, warning = btech_to_chirp(csv_content)
        elif direction == 'clipboard_to_internal':
            internal_channels, warning = clipboard_to_internal_wrapper(csv_content)
            output_csv = internal_to_clipboard(internal_channels)
        else:
            return '<div class="alert alert-danger mb-0">Invalid direction</div>', 400
        
        if not output_csv:
            return '<div class="alert alert-info mb-0">Conversion produced no content</div>', 200

        # For paste, we don't save a file in UPLOAD_FOLDER like upload_file does,
        # but we still want to record it in history.
        input_filename = "pasted_content"
        output_filename = f"pasted_{uuid.uuid4()}.csv"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, 'w') as f:
            f.write(output_csv)
            
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT INTO conversion_history (input_filename, output_filename, status, warning) VALUES (?, ?, ?, ?)',
                (input_filename, output_filename, 'success', warning)
            )
        
        download_url = f"/downloads/{output_filename}"
        warning_html = f'<div class="alert alert-warning mt-2 mb-0">{warning}</div>' if warning else ""
        
        return f'''
        <div class="alert alert-success mb-0">
            uploaded and converted successfully!
            <div class="mt-2">
                <a href="{download_url}" class="btn btn-sm btn-success" download="{output_filename}">Download Converted File</a>
            </div>
        </div>
        {warning_html}
        ''', 200

    except ConversionError as e:
        return f'<div class="alert alert-danger mb-0">Conversion Error: {str(e)}</div>', 400
    except Exception as e:
        import traceback
        print(f"Error in convert_paste: {str(e)}")
        tracemult = traceback.format_exc()
        print(tracemult)
        return f'<div class="alert alert-danger mb-0">Error: {str(e)}</div>', 500

@api_bp.route('/history/fragment', methods=['GET'])
def history_fragment():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT input_filename, output_filename, status, warning, datetime(timestamp, \'localtime\') as timestamp FROM conversion_history ORDER BY timestamp DESC')
    rows = cur.fetchall()
    conn.close()
    
    return render_template('partials/history_fragment.html', history_items=rows)
