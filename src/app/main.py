import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, send_file
import io
from converter.logic import chirp_to_btech, btech_to_chirp, ConversionError
from app.api.routes import api_bp, UPLOAD_FOLDER

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/converter-ui')
def converter_ui():
    return render_template('partials/converter_ui.html')

@app.route('/converter-paste-ui', methods=['GET'])
def converter_paste_ui():
    return render_template('partials/converter_paste_ui.html')

@app.route('/converter-file-ui', methods=['GET'])
def converter_file_ui():
    return render_template('partials/converter_file_ui.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    # Note: UPLOAD_FOLDER should be accessible or we can use the same logic as in routes.py
    # For now, let's just use the path relative to the app root if possible, 
    # but it's safer to define it consistently.
    # Since I don't want to refactor everything yet, I'll use the absolute path if I can.
    # Actually, let's just use the same UPLOAD_FOLDER logic if I can.
    # But I can't access UPLOAD_FOLDER here easily without importing it.
    # Let's just use the same logic as routes.py
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

