from flask import Blueprint, request, jsonify
from converter.logic import chirp_to_btech, ConversionError

api_bp = Blueprint('api', __name__)

@api_bp.route('/convert/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # For now, just return success. Implementation will involve saving file.
        return jsonify({'message': f'File {file.filename} uploaded successfully (mock)'}), 200

@api_bp.route('/convert/paste', methods=['POST'])
def convert_paste():
    data = request.get_json()
    if not data or 'csv_content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    
    csv_content = data['csv_content']
    
    try:
        output_csv, warning = chirp_to_btech(csv_content)
        return jsonify({
            'success': True,
            'output': output_csv,
            'warning': warning
        }), 200
    except ConversionError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/history', methods=['GET'])
def get_history():
    # Placeholder for history retrieval
    return jsonify({'history': []}), 200
