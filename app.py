from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from ml_model import match_resume_to_jobs

UPLOAD_FOLDER = 'resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return "No file part", 400
    file = request.files['resume']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Parse resume
        parsed_data = parse_resume(filepath)

        # Match against job descriptions
        results = match_resume_to_jobs(parsed_data)

        return render_template('results.html', parsed_data=parsed_data, results=results)

    return "Unsupported file type", 400

if __name__ == '__main__':
    app.run(debug=True)

