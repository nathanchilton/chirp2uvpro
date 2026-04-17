import os
import sqlite3
import uuid
import html
from flask import Blueprint, request, jsonify, render_template
from converter.logic import convert_format, ConversionError
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
        return '<div class="alert alert-danger mb-0">No selected file</div>', 400
    
    try:
        input_format = request.form.get('input_format', 'auto')
        output_format = request.form.get('output_format', 'btech')
        
        filename = str(uuid.uuid4()) + "_" + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Read content for conversion
        with open(file_path, 'r') as f:
            csv_content = f.read()
        print(f"DEBUG: csv_content: {csv_content}")
        print(f"DEBUG: upload_file - input_format: {input_format}, output_format: {output_format}")
        
        output_csv, warning = convert_format(csv_content, input_format, output_format)
        
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
        <div class="mb-3">
            <label class="form-label">Result:</label>
            <textarea class="form-control" rows="15" readonly role="textbox">{html.escape(output_csv)}</textarea>
        </div>
        <div class="alert alert-success mb-0">
            File uploaded and converted successfully!
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

        input_format = data.get('input_format', 'auto')
        output_format = data.get('output_format', 'btech')
        print(f"DEBUG: convert_paste - input_format: {input_format}, output_format: {output_format}")
        
        output_csv, warning = convert_format(content, input_format, output_format)
        
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
        <div class="mb-3">
            <label class="form-label">Result:</label>
            <textarea class="form-control" rows="15" readonly role="textbox">{html.escape(output_csv)}</textarea>
        </div>
        <div class="alert alert-success mb-0">
            Content pasted and converted successfully!
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
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return f'<div class="alert alert-danger mb-0">Error: {str(e)}</div>', 500

@api_bp.route('/history/fragment', methods=['GET'])
def history_fragment():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT input_filename, output_filename, status, warning, datetime(timestamp, \'localtime\') as timestamp FROM conversion_history ORDER BY timestamp DESC')
    rows = cur.fetchall()
    conn.close()
    
    return render_template('partials/history_fragment.html', history_items=rows)
