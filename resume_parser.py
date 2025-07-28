import os
import spacy
import pdfplumber
from docx import Document

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_resume(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path)
    else:
        return {"error": "Unsupported file type"}

    doc = nlp(raw_text)

    # Simple extraction logic (expandable)
    skills = []
    education = []
    experience = []

    for ent in doc.ents:
        if ent.label_ == "ORG" or "university" in ent.text.lower():
            education.append(ent.text)
        elif ent.label_ == "DATE":
            experience.append(ent.text)
        elif ent.label_ in ["SKILL", "WORK_OF_ART"]:
            skills.append(ent.text)

    return {
        "text": raw_text,
        "education": list(set(education)),
        "experience": list(set(experience)),
        "skills": list(set(skills))
    }

