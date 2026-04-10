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

@app.route('/health')
def health_check():
    return {"status": "healthy"}, 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/converter-ui')
def converter_ui():
    mode = request.args.get('mode', 'chirp_to_btech')
    return render_template('partials/converter_ui.html', mode=mode)

@app.route('/converter-file-ui', methods=['GET'])
def converter_file_ui():
    return render_template('partials/converter_file_ui.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

