import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, send_file
import io
from converter.logic import chirp_to_btech, btech_to_chirp, ConversionError
from api.routes import api_bp

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/converter-ui', methods=['GET'])
def converter_ui():
    return '''
    <div class="converter-ui">
        <h3 class="converter-title">Convert CSV Content</h3>
        <form hx-post="/api/convert/paste" hx-target="#result" hx-swap="innerHTML" hx-indicator="#loading">
            <textarea name="csv_content" rows="10" style="width: 100%; margin-bottom: 10px;" placeholder="Paste CHIRP CSV content here..." required></textarea>
            <br>
            <button type="submit">Convert to BTECH</button>
        </form>
        <div id="loading" class="htmx-indicator">Converting...</div>
        <div id="result" style="margin-top: 20px; white-space: pre-wrap; text-align: left; font-size: 0.8rem; max-height: 200px; overflow: auto; border: 1px solid #ccc; padding: 5px;">
            Result will appear here.
        </div>
    </div>
    '''

@app.route('/converter-file-ui', methods=['GET'])
def converter_file_ui():
    return '''
    <div class="converter-file-ui">
        <h3 class="converter-title">Upload and Convert CSV</h3>
        <form hx-post="/api/convert/upload" hx-encoding="multipart/form-data" hx-target="#upload-result" hx-swap="innerHTML" hx-indicator="#loading">
            <input type="file" name="file" accept=".csv" required>
            <br><br>
            <button type="submit">Upload and Convert</button>
        </form>
        <div id="loading" class="htmx-indicator">Uploading and converting...</div>
        <div id="upload-result" style="margin-top: 20px; white-space: pre-wrap; text-align: left; font-size: 0.8rem; max-height: 200px; overflow: auto; border: 1px solid #ccc; padding: 5px;">
            Upload a file to begin.
        </div>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)

