from sentence_transformers import SentenceTransformer, util
import json
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

# Load job descriptions
JOB_FILE = 'data/job_descriptions.json'

def load_job_descriptions():
    if os.path.exists(JOB_FILE):
        with open(JOB_FILE, 'r') as f:
            return json.load(f)
    return []

def match_resume_to_jobs(parsed_resume):
    jobs = load_job_descriptions()
    resume_text = parsed_resume['text']
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    ranked_jobs = []

    for job in jobs:
        job_text = job['title'] + " " + job['description']
        job_embedding = model.encode(job_text, convert_to_tensor=True)
        score = util.cos_sim(resume_embedding, job_embedding).item()
        ranked_jobs.append({
            "title": job['title'],
            "description": job['description'],
            "score": round(score * 100, 2)
        })

    ranked_jobs.sort(key=lambda x: x['score'], reverse=True)
    return ranked_jobs

