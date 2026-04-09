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
        
        return jsonify({
            'message': 'Conversion successful',
            'output_filename': output_filename,
            'warning': warning
        }), 200
        
    except ConversionError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/convert/file/<filename>', methods=['POST'])
def convert_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r') as f:
            csv_content = f.read()
            
        output_csv, warning = chirp_to_btech(csv_content)
        
        output_filename = f"converted_{uuid.uuid4()}.csv"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        with open(output_path, 'w') as f:
            f.write(output_csv)
            
        # Log to history
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT INTO conversion_history (input_filename, output_filename, status, warning) VALUES (?, ?, ?, ?)',
                (filename, output_filename, 'success', warning)
            )
            
        return jsonify({
            'message': 'File conversion successful',
            'output_filename': output_filename,
            'warning': warning
        }), 200
        
    except ConversionError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/history', methods=['GET'])
def get_history():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute('SELECT * FROM conversion_history ORDER BY timestamp DESC LIMIT 50')
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(history), 200


