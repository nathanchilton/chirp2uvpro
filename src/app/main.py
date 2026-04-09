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
        <form hx-post="/convert" hx-target="#result" hx-swap="innerHTML" hx-indicator="#loading">
            <textarea name="csv_content" rows="10" style="width: 100%; margin-bottom: 10px;" placeholder="Paste CSV content here..." required></textarea>
            <br>
            <button type="submit">Convert to BTECH</button>
        </form>
        <div id="loading" class="htmx-indicator">Converting...</div>
        <div id="result" style="margin-top: 20px; white-space: pre-wrap; text-align: left; font-size: 0.8rem; max-height: 200px; overflow: auto; border: 1px solid #ccc; padding: 5px;">
            Result will appear here.
        </div>
    </div>
    '''

@app.route('/convert', methods=['POST'])
def convert():
    csv_content = request.form.get('csv_content')
    if not csv_content:
        return "Error: No content provided."
    
    try:
        output_csv, warning = chirp_to_btech(csv_content)
        result_msg = "Conversion successful!"
        if warning:
            result_msg += f"\n\nWARNING: {warning}"
        
        # In a real app, we'd save this to a file or provide a download link.
        # For now, just show success and a snippet.
        snippet = output_csv[:500] + "..." if len(output_csv) > 500 else output_csv
        return f"{result_msg}\n\nPreview:\n{snippet}"
        
    except ConversionError as e:
        return f"Conversion Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)

