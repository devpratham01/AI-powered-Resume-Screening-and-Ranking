import re
import os
import json
import logging
import PyPDF2
import docx
import nltk
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logging.warning("SpaCy model 'en_core_web_sm' not found. Using small language model instead.")
    # If model not installed, use a smaller one or initialize a blank model
    nlp = spacy.blank('en')

# Common skills list - this could be expanded or loaded from a database
COMMON_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "typescript", "go", "scala", "rust",
    # Web Development
    "html", "css", "react", "angular", "vue.js", "node.js", "django", "flask", "express.js", "spring", "asp.net",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite", "redis", "cassandra", "elasticsearch",
    # DevOps & Tools
    "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp", "terraform", "ansible", "ci/cd",
    # Data Science & AI
    "machine learning", "deep learning", "data analysis", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
    "nlp", "computer vision", "big data", "hadoop", "spark", "tableau", "power bi", "r", "matlab",
    # General Business Skills
    "project management", "agile", "scrum", "leadership", "team management", "communication", "problem solving",
    "critical thinking", "time management", "presentation", "public speaking", "microsoft office", "excel"
]

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
    return text

def preprocess_text(text):
    """Preprocess text: lowercase, tokenize, remove stopwords, lemmatize"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    return ' '.join(tokens)

def extract_skills(text):
    """Extract skills from text using NLP and a predefined skills list"""
    skills = []
    preprocessed_text = preprocess_text(text.lower())
    
    # Simple keyword matching from common skills list
    for skill in COMMON_SKILLS:
        if skill.lower() in preprocessed_text:
            skills.append(skill)
    
    # Use spaCy for more advanced NLP (if available)
    try:
        doc = nlp(text.lower())
        # Extract noun phrases as potential skills
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        # Check if any noun phrases might be skills
        for phrase in noun_phrases:
            phrase = phrase.lower().strip()
            # Check if any part of the phrase matches a skill
            for skill in COMMON_SKILLS:
                if skill in phrase and skill not in skills:
                    skills.append(skill)
    except Exception as e:
        logging.error(f"Error in spaCy processing: {e}")
    
    return list(set(skills))  # Remove duplicates

def extract_education(text):
    """Extract education information from text"""
    education = []
    education_keywords = ["bachelor", "master", "phd", "doctorate", "degree", "bs", "ba", "bsc", "msc", "ma", "b.s.", "b.a.", "m.s.", "m.a.", "ph.d."]
    
    # Find sentences containing education keywords
    sentences = re.split(r'[.!?]', text)
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in education_keywords):
            education.append(sentence.strip())
    
    return education

def extract_experience(text):
    """Extract work experience information from text"""
    experience = []
    experience_keywords = ["experience", "work", "job", "position", "role", "profession", "employment", "career"]
    
    # Find paragraphs containing experience keywords
    paragraphs = text.split('\n\n')
    for paragraph in paragraphs:
        if any(keyword in paragraph.lower() for keyword in experience_keywords):
            experience.append(paragraph.strip())
    
    return experience

def calculate_match_score(resume_text, job_description):
    """Calculate a match score between resume and job description using TF-IDF and cosine similarity"""
    # Preprocess texts
    preprocessed_resume = preprocess_text(resume_text)
    preprocessed_job = preprocess_text(job_description)
    
    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([preprocessed_resume, preprocessed_job])
    
    # Calculate cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # Scale to 0-100 percentage
    score = float(similarity * 100)
    
    return score

def get_skills_match(resume_skills, job_skills):
    """Get skills that match between resume and job description"""
    matched_skills = []
    missing_skills = []
    
    for skill in job_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    
    return {
        'matched': matched_skills,
        'missing': missing_skills,
        'match_percentage': len(matched_skills) / len(job_skills) * 100 if job_skills else 0
    }

def analyze_resume(file_path, file_extension, job_description):
    """Analyze resume and calculate match with job description"""
    # Extract text based on file type
    if file_extension.lower() == '.pdf':
        resume_text = extract_text_from_pdf(file_path)
    elif file_extension.lower() == '.docx':
        resume_text = extract_text_from_docx(file_path)
    else:
        return {"error": "Unsupported file format"}
    
    if not resume_text:
        return {"error": "Could not extract text from file"}
    
    # Extract information from resume
    resume_skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    experience = extract_experience(resume_text)
    
    # Extract skills from job description
    job_skills = extract_skills(job_description)
    
    # Calculate match score
    match_score = calculate_match_score(resume_text, job_description)
    
    # Get skills match details
    skills_match = get_skills_match(resume_skills, job_skills)
    
    return {
        "resume_text": resume_text,
        "skills": resume_skills,
        "education": education,
        "experience": experience,
        "match_score": match_score,
        "skills_match": skills_match
    }
