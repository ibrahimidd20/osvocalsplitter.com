from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import spleeter
from spleeter.separator import Separator
from werkzeug.utils import secure_filename
from pydub import AudioSegment

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

separator = Separator('spleeter:2stems')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            output_dir = os.path.join(app.config['OUTPUT_FOLDER'], filename.split('.')[0])
            separator.separate_to_file(file_path, output_dir)

            return jsonify({'filename': filename.split('.')[0]})

    return render_template('index.html')

@app.route('/download/<filename>/<filetype>')
def download(filename, filetype):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename, f'{filetype}.wav')
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(app.config['OUTPUT_FOLDER'], filename), f'{filetype}.wav')
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
