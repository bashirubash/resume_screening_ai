import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

def preprocess_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word.isalnum() and word not in stopwords.words('english')]
    return ' '.join(tokens)

def load_job_descriptions():
    with open('sample_data/job_descriptions.json', 'r') as file:
        return json.load(file)

def match_resume_to_jobs(resume_text):
    jobs = load_job_descriptions()
    corpus = [preprocess_text(job["description"]) for job in jobs]
    resume_cleaned = preprocess_text(resume_text)
    corpus.append(resume_cleaned)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(corpus)

    resume_vector = vectors[-1]
    job_vectors = vectors[:-1]

    similarities = cosine_similarity(resume_vector, job_vectors).flatten()
    match_results = []

    for idx, score in enumerate(similarities):
        match_results.append({
            "title": jobs[idx]["title"],
            "score": round(score * 100, 2)
        })

    # Sort by top scores
    return sorted(match_results, key=lambda x: x['score'], reverse=True)
