from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import logging
from resume_parser import parse_resume
from ml_model import match_resume_to_jobs

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'resumes'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applicants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Logging setup
logging.basicConfig(filename='app.log', level=logging.INFO)

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- DB Model ---
class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    matched_job = db.Column(db.String(120))
    score = db.Column(db.Float)

# --- Routes ---

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['resume']
    name = request.form['name']
    email = request.form['email']

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        extracted_data = parse_resume(filepath)
        matches = match_resume_to_jobs(extracted_data)

        # Save best match
        if matches:
            top_match = matches[0]
            new_applicant = Applicant(
                name=name,
                email=email,
                matched_job=top_match['title'],
                score=top_match['score']
            )
            db.session.add(new_applicant)
            db.session.commit()
            logging.info(f'New applicant {name} matched with {top_match["title"]}')
        else:
            logging.info(f'New applicant {name} had no matches.')

        return render_template('results.html', matches=matches)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'Admin123':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials"
            logging.warning("Failed admin login attempt.")
    return render_template('admin_login.html', error=error)

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    applicants = Applicant.query.all()
    return render_template('admin_dashboard.html', applicants=applicants)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('upload_form'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
