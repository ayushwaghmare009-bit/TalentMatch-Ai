import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text.strip()

def calculate_match_score(job_description, resume_text):
    if not resume_text or not job_description:
        return 0.0
    
    documents = [job_description, resume_text]
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity[0][0]) * 100
        return round(score, 2)
    except Exception:
        return 0.0