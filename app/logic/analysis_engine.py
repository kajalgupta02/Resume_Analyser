"""Pure resume-analysis rules and optional NLP adapters."""

from __future__ import annotations

import math
import re
from functools import lru_cache
from typing import Any, Mapping

from .constants import BOILERPLATE_STOPWORDS, COMMON_INDUSTRY_SKILLS
from .models import ResumeAnalysisResult


def _clean_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


@lru_cache(maxsize=1)
def _load_spacy_nlp():
    try:
        import spacy
    except Exception:
        return None
    for model_name in ("en_core_web_sm", "en_core_web_md", "en_core_web_lg"):
        try:
            return spacy.load(model_name)
        except Exception:
            continue
    return None


@lru_cache(maxsize=1)
def _load_sentence_transformer_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def _ensure_nltk_data() -> None:
    import nltk
    try:
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)


def _safe_similarity(cleaned_resume: str, cleaned_jd: str) -> float:
    if not cleaned_resume.strip() or not cleaned_jd.strip():
        return 0.0
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        matrix = TfidfVectorizer(stop_words="english").fit_transform([cleaned_resume, cleaned_jd])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:
        return 0.0


def _safe_semantic_similarity(resume_text: str, job_description_text: str) -> tuple[float | None, bool]:
    if not resume_text.strip() or not job_description_text.strip():
        return None, False
    model = _load_sentence_transformer_model()
    if model is None:
        return None, False
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        embeddings = model.encode([resume_text, job_description_text], normalize_embeddings=True)
        return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]), True
    except Exception:
        return None, False


def _display_skill(skill: str) -> str:
    acronyms = {"aws", "sql", "api", "apis", "ci/cd", "cicd", "k8s", "nlp", "ui/ux", "seo", "tdd", "oop", "gcp", "r"}
    return " ".join(word.upper() if word in acronyms else word.capitalize() for word in skill.split())


def _keyword_pattern(keyword: str) -> str:
    aliases = {
        "rest apis": r"\b(rest|restful|rest api|rest apis)\b", "rest api": r"\b(rest|restful|rest api|rest apis)\b",
        "ci/cd": r"\b(ci/cd|cicd|continuous integration|continuous deployment)\b", "cicd": r"\b(ci/cd|cicd|continuous integration|continuous deployment)\b",
        "kubernetes": r"\b(kubernetes|k8s)\b", "k8s": r"\b(kubernetes|k8s)\b", "react": r"\b(react|reactjs|react\.js)\b", "react.js": r"\b(react|reactjs|react\.js)\b",
        "node.js": r"\b(node|nodejs|node\.js)\b", "node": r"\b(node|nodejs|node\.js)\b", "aws": r"\b(aws|amazon web services)\b", "gcp": r"\b(gcp|google cloud)\b",
    }
    return aliases.get(keyword, r"\b" + re.escape(keyword) + r"\b")


def _extract_skills_and_keywords(job_description_text: str, resume_text: str) -> tuple[list[str], list[str], list[str]]:
    if not job_description_text.strip() or not resume_text.strip():
        return [], [], []
    lower_jd, lower_resume = job_description_text.lower(), resume_text.lower()
    found, seen = [], set()
    for skill in COMMON_INDUSTRY_SKILLS:
        if re.search(r"\b" + re.escape(skill) + r"\b", lower_jd):
            display = _display_skill(skill)
            if display.lower() not in seen:
                seen.add(display.lower()); found.append(display)
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=35)
        matrix = vectorizer.fit_transform([_clean_text(job_description_text)])
        for index in matrix.toarray()[0].argsort()[::-1]:
            term = vectorizer.get_feature_names_out()[index].strip()
            if len(term) < 3 or term.isdigit() or term in BOILERPLATE_STOPWORDS or any(word in BOILERPLATE_STOPWORDS for word in term.split()):
                continue
            display = " ".join(word.capitalize() for word in term.split())
            if display.lower() not in seen:
                seen.add(display.lower()); found.append(display)
            if len(found) >= 15:
                break
    except Exception:
        pass
    if not found:
        found = ["Technical Skills", "Communication", "Problem Solving", "Collaboration"]
    present = [skill for skill in found if re.search(_keyword_pattern(skill.lower()), lower_resume)]
    return found, present, [skill for skill in found if skill not in present]


def _detect_sections_with_regex(resume_text: str, config: Mapping[str, Any]) -> dict[str, bool]:
    return {name: bool(re.search(r"(?:" + "|".join(re.escape(item) for item in values) + r")", resume_text, re.IGNORECASE)) for name, values in config.get("section_headers", {}).items()}


def _detect_sections(resume_text: str, config: Mapping[str, Any]) -> dict[str, bool]:
    sections = _detect_sections_with_regex(resume_text, config)
    nlp = _load_spacy_nlp()
    if nlp is None:
        return sections
    nlp(resume_text)  # Preserve optional spaCy model loading and processing behavior.
    lower_resume, cleaned = resume_text.lower(), _clean_text(resume_text)
    headers = config.get("section_headers", {})
    if not sections.get("Contact Info"):
        sections["Contact Info"] = bool(re.search(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", resume_text) or re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", resume_text) or any(word in lower_resume for word in headers.get("Contact Info", [])))
    if not sections.get("Education"):
        sections["Education"] = bool(any(word in lower_resume for word in headers.get("Education", [])) or re.search(r"\b(bsc|msc|phd|ba|bs|associate|bachelor|master|degree|university|college)\b", lower_resume))
    if not sections.get("Experience"):
        sections["Experience"] = bool(any(word in lower_resume for word in headers.get("Experience", [])) or any(verb in cleaned for verb in config.get("action_verbs", [])))
    if not sections.get("Skills"):
        sections["Skills"] = bool(any(word in cleaned for word in headers.get("Skills", [])))
    return sections


def _build_suggestions(score: float, missing: list[str], verbs: list[str], metrics: int, word_count: int, sections: Mapping[str, bool]) -> list[str]:
    suggestions = []
    if missing: suggestions.append(f"Add key target skills naturally into your experience: {', '.join(missing[:3])}.")
    if len(verbs) < 4: suggestions.append("Strengthen your bullet points using action verbs like 'Architected', 'Spearheaded', 'Optimized', or 'Engineered'.")
    if metrics < 2: suggestions.append("Quantify your achievements with measurable results (e.g., 'Reduced query latency by 35%').")
    if word_count > 800: suggestions.append("Your resume is slightly lengthy. Aim for a concise, high-impact 1-2 page structure.")
    elif word_count < 250: suggestions.append("Your resume seems short. Elaborate on project deliverables, responsibilities, and technical tools.")
    suggestions.extend(f"Add a distinct '{name}' section header to ensure ATS parsers classify your credentials accurately." for name, present in sections.items() if not present)
    return suggestions or ["Your resume is well-tailored. Keep impact metrics and strongest technical achievements near the top."]


def calculate_ats_match_score(present_keywords: list[str], jd_keywords: list[str], raw_tfidf_similarity: float, sections: Mapping[str, bool], action_verbs: list[str], quantifiable_metrics: int) -> float:
    skills_ratio = len(present_keywords) / len(jd_keywords) if jd_keywords else 0.85
    relevance = min(1.0, math.sqrt(raw_tfidf_similarity) * 1.35) if raw_tfidf_similarity > 0 else 0.40
    section_ratio = sum(sections.values()) / max(1, len(sections)) if sections else 1.0
    health = min(1.0, (section_ratio * .7) + (min(1.0, len(action_verbs) / 4) * .2) + (.1 if quantifiable_metrics > 0 else 0))
    return round(max(.10, min(.98, (skills_ratio * .60) + (relevance * .25) + (health * .15))), 3)


def analyze_resume(resume_text: str, job_description_text: str, config: Mapping[str, Any], similarity_mode: str = "tfidf") -> ResumeAnalysisResult:
    mode = similarity_mode.lower().strip() if similarity_mode.lower().strip() in {"tfidf", "semantic"} else "tfidf"
    if not resume_text or not job_description_text:
        return ResumeAnalysisResult(similarity_mode=mode, similarity_score=0.0, word_count=0, readability=0.0)
    _ensure_nltk_data()
    cleaned_resume = _clean_text(resume_text)
    words = resume_text.split(); word_count = len(words)
    sentences = len([part for part in re.split(r"[.!?]+", resume_text) if part.strip()]) or 1
    readability = max(0.0, min(100.0, 100 - ((sum(map(len, words)) / word_count if word_count else 0) * 10) - (word_count / sentences)))
    tfidf = _safe_similarity(cleaned_resume, _clean_text(job_description_text))
    semantic, available = _safe_semantic_similarity(resume_text, job_description_text)
    jd, present, missing = _extract_skills_and_keywords(job_description_text, resume_text)
    sections = _detect_sections(resume_text, config)
    verbs = [verb for verb in config.get("action_verbs", []) if verb in cleaned_resume]
    metrics = len(re.findall(r"\b\d+\%?\b|\$[\d,]+", resume_text))
    score = calculate_ats_match_score(present, jd, tfidf, sections, verbs, metrics)
    return ResumeAnalysisResult(similarity_mode=mode, similarity_score=score, tfidf_similarity_score=tfidf, semantic_similarity_score=semantic, semantic_similarity_available=available, word_count=word_count, readability=readability, jd_keywords=jd, present_keywords=present, missing_keywords=missing, action_verbs=verbs, quantifiable_metrics=metrics, sections=dict(sections), suggestions=_build_suggestions(score, missing, verbs, metrics, word_count, sections))
