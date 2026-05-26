import os
import fitz  # PyMuPDF
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import re

class ResumeAnalyser:
    def __init__(self):
        self.resume_text = ""
        self.job_description = ""
        self.results = {}
        self._nltk_initialized = False
        
        self.job_roles = {
            "Data Analyst": ["python", "sql", "excel", "statistics", "visualization", "pandas", "tableau", "power bi"],
            "Backend Developer": ["python", "java", "databases", "api", "rest", "docker", "git", "aws"],
            "Frontend Developer": ["javascript", "html", "css", "react", "vue", "typescript", "responsive design"],
            "Data Scientist": ["python", "r", "machine learning", "deep learning", "statistics", "sql", "tensorflow"],
            "DevOps Engineer": ["docker", "kubernetes", "jenkins", "aws", "ci/cd", "linux", "terraform"],
        }

    def _ensure_nltk_data(self):
        """Lazy load NLTK data to improve startup speed"""
        if not self._nltk_initialized:
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
            except LookupError:
                # Only download if missing, and do it quietly
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            self._nltk_initialized = True

    def load_resume(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                self.resume_text = f.read()
        elif ext == '.docx':
            doc = Document(file_path)
            self.resume_text = '\n'.join([p.text for p in doc.paragraphs])
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            self.resume_text = text
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        return self.resume_text

    def set_job_description(self, text):
        self.job_description = text

    def analyze(self):
        if not self.resume_text or not self.job_description:
            return None

        self._ensure_nltk_data()
        
        # Basic text cleaning
        def clean_text(text):
            text = text.lower()
            text = re.sub(r'[^a-z0-9\s]', ' ', text)
            return text

        cleaned_resume = clean_text(self.resume_text)
        cleaned_jd = clean_text(self.job_description)

        # Advanced Metrics
        word_count = len(self.resume_text.split())
        sentence_count = len(re.split(r'[.!?]+', self.resume_text))
        avg_word_len = sum(len(word) for word in self.resume_text.split()) / word_count if word_count > 0 else 0
        
        # Simple readability score (mock Flesch-Kincaid)
        readability = 100 - (avg_word_len * 10) - (word_count / sentence_count * 1.0)
        readability = max(0, min(100, readability))

        # TF-IDF Similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        # Keyword Extraction
        feature_names = vectorizer.get_feature_names_out()
        jd_tfidf = tfidf_matrix[1].toarray()[0]
        
        keyword_indices = jd_tfidf.argsort()[::-1][:20]
        important_keywords = [feature_names[i] for i in keyword_indices if jd_tfidf[i] > 0]
        
        # Check presence in resume
        resume_words = set(cleaned_resume.split())
        missing_keywords = [kw for kw in important_keywords if kw not in resume_words]
        present_keywords = [kw for kw in important_keywords if kw in resume_words]

        # Section detection (Impactful for UI)
        sections = {
            "Contact Info": bool(re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b|\b\d{10}\b', self.resume_text)),
            "Education": bool(re.search(r'education|university|college|degree|bachelor|master', self.resume_text, re.I)),
            "Experience": bool(re.search(r'experience|work|employment|history|professional', self.resume_text, re.I)),
            "Skills": bool(re.search(r'skills|technologies|proficiencies|expertise', self.resume_text, re.I))
        }

        # --- Action Verb Analysis ---
        action_verbs = ['managed', 'led', 'developed', 'created', 'implemented', 'achieved', 'improved', 'negotiated', 'streamlined', 'spearheaded', 'architected', 'engineered', 'drove', 'pioneered']
        found_verbs = [verb for verb in action_verbs if verb in cleaned_resume]

        # --- Quantifiable Metrics Analysis ---
        quantifiable_metrics = len(re.findall(r'\b\d+\%?\b|\$[\d,]+', self.resume_text))

        # --- Generate Suggestions ---
        suggestions = []
        if similarity < 0.4:
            suggestions.append("Your resume has a low keyword match. Tailor your resume by incorporating more terms from the job description.")
        if len(missing_keywords) > 5:
            suggestions.append(f"You're missing several key terms like '{', '.join(missing_keywords[:3])}...'. Find places to add these naturally.")
        if len(found_verbs) < 5:
            suggestions.append("Strengthen your experience section by using more powerful action verbs like 'developed', 'managed', or 'spearheaded'.")
        if quantifiable_metrics < 2:
            suggestions.append("Add more quantifiable achievements. Instead of 'improved performance', try 'improved performance by 15%'.")
        if word_count > 700:
            suggestions.append("Your resume is a bit long. Aim for a concise, one-page resume unless you have over 10 years of experience.")
        elif word_count < 300:
            suggestions.append("Your resume seems a bit short. Ensure you've detailed your experiences and skills adequately.")

        self.results = {
            "similarity_score": similarity,
            "word_count": word_count,
            "readability": readability,
            "jd_keywords": important_keywords,
            "present_keywords": present_keywords,
            "missing_keywords": missing_keywords,
            "action_verbs": found_verbs,
            "quantifiable_metrics": quantifiable_metrics,
            "suggestions": suggestions
        }
        
        return self.results

    def generate_recommendations(self, similarity, missing_keywords, sections):
        recommendations = []
        
        # Section based recommendations
        for section, present in sections.items():
            if not present:
                recommendations.append(f"Crucial section missing: {section}. Add it to look professional!")

        if similarity < 0.5:
            recommendations.append("Your resume match score is quite low. Consider significantly tailoring your content to the job description.")
        
        if missing_keywords:
            recommendations.append(f"Sprinkle in these missing keywords: {', '.join(missing_keywords[:5])}")
            recommendations.append("Don't just list skills; show how you used them to create impact.")
        
        if len(self.resume_text.split()) < 200:
            recommendations.append("Your resume is a bit thin. Elaborate more on your achievements.")
        elif len(self.resume_text.split()) > 1000:
            recommendations.append("Your resume is getting a bit long. Aim for concise, punchy bullet points.")
        
        return recommendations
