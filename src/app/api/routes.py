import os
import sqlite3
import uuid
from flask import Blueprint, request, jsonify
from converter.logic import chirp_to_btech, ConversionError
from database import get_db_connection

api_bp = Blueprint('api', __name__)
# Use absolute path or relative to app root for consistency
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'app', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_bp.route('/convert/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        filename = str(uuid.uuid4()) + "_" + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT INTO uploaded_files (filename, file_path) VALUES (?, ?)',
                (file.filename, file_path)
            )
        
        return jsonify({'message': f'File {file.filename} uploaded successfully', 'file_id': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/convert/paste', methods=['POST'])
def convert_paste():
    data = request.get_json()
    if not data or 'csv_content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    
    csv_content = data['csv_content']
    
    try:
        output_csv, warning = chirp_to_btech(csv_content)
        
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
                ('pasted_content', output_filename, 'success', warning)
            )
        
    except ConversionError as e:
        return f'<div style="color: #ff4d4d;"><strong>Error:</strong> {str(e)}</div>', 400
    except Exception as e:
        return f'<div style="color: #ff4d4d;"><strong>Unexpected Error:</strong> {str(e)}</div>', 500


