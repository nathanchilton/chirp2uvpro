import os
import sqlite3
import uuid
from flask import Blueprint, request, jsonify
from converter.logic import chirp_to_btech, btech_to_chirp, ConversionError
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
        else:
            output_csv, warning = btech_to_chirp(csv_content)

        if not output_csv:
            return '<div class="alert alert-info mb-0">Conversion produced no content</div>', 200

        # Create output filename
        output_filename = f"converted_{uuid.uuid4()}.csv"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, 'w') as f:
            f.write(output_csv)
            
        # Log to history
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT INTO conversion_history (input_filename, output_filename, status, warning) VALUES (?, ?, ?, ?)',
                (file.filename, output_filename, 'success', warning)
            )
        
        # Prepare response HTML
        download_url = f"/downloads/{output_filename}"
        warning_html = f'<div class="alert alert-warning mt-2 mb-0">{warning}</div>' if warning else ""
        
        return f'''
        <div class="alert alert-success mb-0">
            File {file.filename} uploaded and converted successfully!
            <div class="mt-2">
                <a href="{download_url}" class="btn btn-sm btn-success" download>Download Converted File</a>
            </div>
        </div>
        {warning_html}
        ''', 200
    except ConversionError as e:
        return f'<div class="alert alert-danger mb-0">Conversion Error: {str(e)}</div>', 400
    except Exception as e:
        return f'<div class="alert alert-danger mb-0">Error: {str(e)}</div>', 500

@api_bp.route('/convert/paste-btech', methods=['POST'])
def convert_paste_btech():
    return convert_paste(direction='btech_to_chirp')

@api_bp.route('/convert/paste', methods=['POST'])
def convert_paste(direction='chirp_to_btech'):
    # Check if it's a form submission (HTMX) or JSON
    if request.form:
        csv_content = request.form.get('csv_content')
        direction = request.form.get('direction', direction)
    else:
        data = request.get_json(silent=True)
        if data is None:
            try:
                data = request.get_data(as_text=True)
                import json
                data = json.loads(data)
            except Exception:
                return '<div class="alert alert-danger mb-0">Invalid JSON or missing Content-Type: application/json header</div>', 415
        
        if not data or 'csv_content' not in data:
            return '<div class="alert alert-danger mb-0">No content provided</div>', 400
        
        csv_content = data['csv_content']
        direction = data.get('direction', direction)


    if not csv_content:
        return '<div class="alert alert-danger mb-0">No content provided</div>', 400

    # Use the direction provided in the request, but allow override from the route if needed
    try:
        if direction == 'chirp_to_btech':
            output_csv, warning = chirp_to_btech(csv_content)
        elif direction == 'b2ch':
            output_csv, warning = btech_to_chirp(csv_content)
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
                ('pasted_content', output_filename, 'success', warning)
            )
        
        download_url = f"/downloads/{output_filename}"
        warning_html = f'<div class="alert alert-warning mt-2 mb-0">{warning}</div>' if warning else ""
        
        return f'''
        <div class="alert alert-success mb-0">
            Conversion successful!
            <div class="mt-2">
                <a href="{download_url}" class="btn btn-sm btn-success" download="{output_filename}">Download Converted File</a>
            </div>
        </div>
        {warning_html}
        ''', 200
        
    except ConversionError as e:
        return f'<div class="alert alert-danger mb-0">Conversion Error: {str(e)}</div>', 400
    except Exception as e:
        return f'<div class="alert alert-danger mb-0">Error: {str(e)}</div>', 500


