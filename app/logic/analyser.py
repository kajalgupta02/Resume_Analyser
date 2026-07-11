from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import fitz  # PyMuPDF
import nltk
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_CONFIG_PATH = Path(__file__).with_name("analysis_config.json")


@dataclass(slots=True)
class ResumeAnalysisResult:
    similarity_score: float
    word_count: int
    readability: float
    jd_keywords: list[str] = field(default_factory=list)
    present_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    action_verbs: list[str] = field(default_factory=list)
    quantifiable_metrics: int = 0
    sections: dict[str, bool] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)


def _normalize_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve()


@lru_cache(maxsize=4)
def load_analysis_config(config_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    resolved_path = _normalize_path(config_path or DEFAULT_CONFIG_PATH)
    with resolved_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    if not isinstance(config, dict):
        raise ValueError("Analysis config must be a JSON object")

    return config


def _compile_patterns(config: Mapping[str, Any]) -> dict[str, re.Pattern[str]]:
    section_headers = config.get("section_headers", {})
    compiled_patterns: dict[str, re.Pattern[str]] = {}

    for section_name, keywords in section_headers.items():
        escaped_keywords = [re.escape(keyword) for keyword in keywords]
        compiled_patterns[section_name] = re.compile(r"(?:" + r"|".join(escaped_keywords) + r")", re.IGNORECASE)

    return compiled_patterns


def _ensure_nltk_data() -> None:
    try:
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)


def load_resume_text(file_path: str | os.PathLike[str]) -> str:
    resolved_path = _normalize_path(file_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"File not found: {resolved_path}")

    ext = resolved_path.suffix.lower()
    if ext == ".txt":
        return resolved_path.read_text(encoding="utf-8")

    if ext == ".docx":
        document = Document(str(resolved_path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    if ext == ".pdf":
        try:
            document = fitz.open(str(resolved_path))
        except Exception as exc:
            raise ValueError(f"Unable to open PDF file: {resolved_path}") from exc

        extracted_text = []
        try:
            for page in document:
                extracted_text.append(page.get_text())
        finally:
            document.close()
        return "".join(extracted_text)

    raise ValueError(f"Unsupported file format: {ext}")


def _clean_text(text: str) -> str:
    text = text.lower()
    return re.sub(r"[^a-z0-9\s]", " ", text)


def _safe_similarity(cleaned_resume: str, cleaned_jd: str) -> float:
    if not cleaned_resume.strip() or not cleaned_jd.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
    except ValueError:
        return 0.0

    return float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])


def _extract_keywords(cleaned_jd: str, cleaned_resume: str) -> tuple[list[str], list[str], list[str]]:
    if not cleaned_resume.strip() or not cleaned_jd.strip():
        return [], [], []

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
    except ValueError:
        return [], [], []

    feature_names = vectorizer.get_feature_names_out()
    jd_tfidf = tfidf_matrix[1].toarray()[0]
    keyword_indices = jd_tfidf.argsort()[::-1][:20]
    important_keywords = [feature_names[index] for index in keyword_indices if jd_tfidf[index] > 0]

    resume_words = set(cleaned_resume.split())
    missing_keywords = [keyword for keyword in important_keywords if keyword not in resume_words]
    present_keywords = [keyword for keyword in important_keywords if keyword in resume_words]
    return important_keywords, present_keywords, missing_keywords


def _detect_sections(resume_text: str, config: Mapping[str, Any]) -> dict[str, bool]:
    section_patterns = _compile_patterns(config)
    sections: dict[str, bool] = {}

    for section_name, pattern in section_patterns.items():
        sections[section_name] = bool(pattern.search(resume_text))

    return sections


def _count_action_verbs(cleaned_resume: str, config: Mapping[str, Any]) -> list[str]:
    action_verbs = config.get("action_verbs", [])
    return [verb for verb in action_verbs if verb in cleaned_resume]


def _count_quantifiable_metrics(resume_text: str) -> int:
    return len(re.findall(r"\b\d+\%?\b|\$[\d,]+", resume_text))


def _build_suggestions(
    similarity_score: float,
    missing_keywords: list[str],
    action_verbs: list[str],
    quantifiable_metrics: int,
    word_count: int,
    sections: Mapping[str, bool],
) -> list[str]:
    suggestions: list[str] = []

    if similarity_score < 0.4:
        suggestions.append("Your resume has a low keyword match. Tailor your resume by incorporating more terms from the job description.")

    if len(missing_keywords) > 5:
        suggestions.append(f"You're missing several key terms like '{', '.join(missing_keywords[:3])}...'. Find places to add these naturally.")

    if len(action_verbs) < 5:
        suggestions.append("Strengthen your experience section by using more powerful action verbs like 'developed', 'managed', or 'spearheaded'.")

    if quantifiable_metrics < 2:
        suggestions.append("Add more quantifiable achievements. Instead of 'improved performance', try 'improved performance by 15%'.")

    if word_count > 700:
        suggestions.append("Your resume is a bit long. Aim for a concise, one-page resume unless you have over 10 years of experience.")
    elif word_count < 300:
        suggestions.append("Your resume seems a bit short. Ensure you've detailed your experiences and skills adequately.")

    for section_name, present in sections.items():
        if not present:
            suggestions.append(f"Add a clear {section_name.lower()} section to improve structure and ATS readability.")

    return suggestions


def analyze_resume(
    resume_text: str,
    job_description_text: str,
    config: Mapping[str, Any],
) -> ResumeAnalysisResult:
    if not resume_text or not job_description_text:
        return ResumeAnalysisResult(
            similarity_score=0.0,
            word_count=0,
            readability=0.0,
        )

    _ensure_nltk_data()

    cleaned_resume = _clean_text(resume_text)
    cleaned_jd = _clean_text(job_description_text)

    word_count = len(resume_text.split())
    sentence_count = len([segment for segment in re.split(r"[.!?]+", resume_text) if segment.strip()])
    sentence_count = sentence_count or 1
    avg_word_len = sum(len(word) for word in resume_text.split()) / word_count if word_count > 0 else 0

    readability = 100 - (avg_word_len * 10) - (word_count / sentence_count * 1.0)
    readability = max(0.0, min(100.0, readability))

    similarity_score = _safe_similarity(cleaned_resume, cleaned_jd)
    jd_keywords, present_keywords, missing_keywords = _extract_keywords(cleaned_jd, cleaned_resume)
    sections = _detect_sections(resume_text, config)
    action_verbs = _count_action_verbs(cleaned_resume, config)
    quantifiable_metrics = _count_quantifiable_metrics(resume_text)
    suggestions = _build_suggestions(
        similarity_score,
        missing_keywords,
        action_verbs,
        quantifiable_metrics,
        word_count,
        sections,
    )

    return ResumeAnalysisResult(
        similarity_score=similarity_score,
        word_count=word_count,
        readability=readability,
        jd_keywords=jd_keywords,
        present_keywords=present_keywords,
        missing_keywords=missing_keywords,
        action_verbs=action_verbs,
        quantifiable_metrics=quantifiable_metrics,
        sections=dict(sections),
        suggestions=suggestions,
    )


class ResumeAnalyser:
    def __init__(self, config_path: str | os.PathLike[str] | None = None):
        self.config = load_analysis_config(config_path)
        self.resume_text = ""
        self.job_description = ""
        self.results = ResumeAnalysisResult(similarity_score=0.0, word_count=0, readability=0.0)
        self.job_roles = self.config.get("job_roles", {})

    def load_resume(self, file_path: str | os.PathLike[str]) -> str:
        self.resume_text = load_resume_text(file_path)
        return self.resume_text

    def set_job_description(self, text: str) -> None:
        self.job_description = text

    def analyze(self) -> dict[str, Any]:
        self.results = analyze_resume(self.resume_text, self.job_description, self.config)
        return asdict(self.results)

    def generate_recommendations(self, similarity, missing_keywords, sections):
        self.results = analyze_resume(self.resume_text, self.job_description, self.config)
        return self.results.suggestions