# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import hashlib
import os
import re
import math
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping
from urllib import error as urllib_error
from urllib import request as urllib_request

import fitz  # PyMuPDF
import nltk
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_CONFIG_PATH = Path(__file__).with_name("analysis_config.json")
DEFAULT_LLM_CACHE_PATH = Path(__file__).resolve().parents[2] / "resume_llm_feedback_cache.json"
DEFAULT_LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_LLM_MODEL = "gpt-4o-mini"


# Comprehensive industry skills & domain keywords taxonomy
COMMON_INDUSTRY_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust", "php", "ruby", "kotlin", "swift", "sql", "r", "html", "css", "bash", "shell",
    # Frameworks & Libraries
    "react", "react.js", "next.js", "angular", "vue", "vue.js", "node.js", "express", "django", "flask", "fastapi", "spring boot", "asp.net", "dotnet",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "keras", "opencv", "redux", "tailwind", "tailwind css", "bootstrap", "graphql", "flutter", "react native",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ci/cd", "cicd", "jenkins", "github actions", "gitlab", "ansible", "helm", "linux", "unix", "nginx", "prometheus", "grafana", "microservices", "serverless", "cloudformation",
    # Databases & Big Data
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "oracle", "cassandra", "sqlite", "kafka", "rabbitmq", "apache spark", "spark", "hadoop", "snowflake", "bigquery",
    # Architecture, Methodologies & Tools
    "rest api", "rest apis", "restful", "restful apis", "git", "github", "gitlab", "agile", "scrum", "kanban", "jira", "unit testing", "integration testing", "tdd", "system design", "system architecture", "oop", "object oriented programming", "data structures", "algorithms",
    # Design, Analytics & Product
    "figma", "ui/ux", "ui design", "ux design", "wireframing", "prototyping", "web accessibility", "wcag", "seo", "a/b testing", "machine learning", "deep learning", "nlp", "natural language processing", "computer vision", "business intelligence", "tableau", "power bi", "excel", "product management", "product roadmap", "data analysis", "data visualization"
]

# Filler words to ignore when dynamically parsing job descriptions
BOILERPLATE_STOPWORDS = {
    "opportunity", "equal", "employer", "candidate", "responsibilities", "requirements", "qualification",
    "qualifications", "experience", "years", "role", "looking", "company", "team", "work", "working",
    "join", "help", "ideal", "successful", "environment", "benefits", "position", "apply", "seeking",
    "must", "able", "strong", "excellent", "demonstrated", "knowledge", "understanding", "good", "great",
    "degree", "bachelor", "master", "equivalent", "related", "field", "skills", "ability", "duties",
    "including", "responsible", "well", "plus", "required", "preferred", "competitive", "package"
}


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _truncate_text(text: str, limit: int = 900) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


@dataclass(slots=True)
class ResumeAnalysisResult:
    similarity_score: float
    word_count: int
    readability: float
    similarity_mode: str = "tfidf"
    tfidf_similarity_score: float = 0.0
    semantic_similarity_score: float | None = None
    semantic_similarity_available: bool = False
    jd_keywords: list[str] = field(default_factory=list)
    present_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    action_verbs: list[str] = field(default_factory=list)
    quantifiable_metrics: int = 0
    sections: dict[str, bool] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)
    llm_feedback: list[str] = field(default_factory=list)
    llm_feedback_enabled: bool = False
    llm_feedback_cached: bool = False
    llm_feedback_error: str | None = None
    llm_feedback_model: str | None = None


@dataclass(slots=True)
class LLMFeedbackConfig:
    enabled: bool
    api_key: str
    endpoint: str = DEFAULT_LLM_ENDPOINT
    model: str = DEFAULT_LLM_MODEL
    cache_path: Path = DEFAULT_LLM_CACHE_PATH
    timeout_seconds: float = 20.0
    max_suggestions: int = 4
    prompt_version: str = "phase3-v1"


@dataclass(slots=True)
class LLMFeedbackResult:
    suggestions: list[str] = field(default_factory=list)
    cached: bool = False
    enabled: bool = False
    error_message: str | None = None
    model: str | None = None


def _normalize_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve()


def _normalize_llm_suggestions(suggestions: list[str]) -> list[str]:
    cleaned_suggestions: list[str] = []
    seen_suggestions: set[str] = set()

    for suggestion in suggestions:
        cleaned_suggestion = suggestion.strip()
        if not cleaned_suggestion or cleaned_suggestion in seen_suggestions:
            continue

        seen_suggestions.add(cleaned_suggestion)
        cleaned_suggestions.append(cleaned_suggestion)

    return cleaned_suggestions


def _extract_resume_bullets(resume_text: str, action_verbs: list[str], limit: int = 8) -> list[str]:
    bullet_pattern = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.*)$")
    resume_bullets: list[str] = []

    for raw_line in resume_text.splitlines():
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue

        bullet_match = bullet_pattern.match(stripped_line)
        if bullet_match:
            candidate = bullet_match.group(1).strip()
        elif len(stripped_line.split()) >= 6 and any(verb in stripped_line.lower() for verb in action_verbs):
            candidate = stripped_line
        else:
            continue

        if candidate and candidate not in resume_bullets:
            resume_bullets.append(candidate)

        if len(resume_bullets) >= limit:
            return resume_bullets

    if resume_bullets:
        return resume_bullets

    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", resume_text) if segment.strip()]
    for sentence in sentences[:limit]:
        resume_bullets.append(sentence)

    return resume_bullets


def _build_llm_cache_key(
    resume_bullets: list[str],
    job_description_text: str,
    config: LLMFeedbackConfig,
) -> str:
    cache_payload = {
        "endpoint": config.endpoint,
        "model": config.model,
        "prompt_version": config.prompt_version,
        "resume_bullets": resume_bullets,
        "job_description_text": job_description_text,
        "max_suggestions": config.max_suggestions,
    }
    serialized_payload = json.dumps(cache_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(serialized_payload).hexdigest()


def _parse_llm_feedback_content(content: str, max_suggestions: int) -> list[str]:
    content = content.strip()
    if not content:
        return []

    try:
        parsed_content = json.loads(content)
    except json.JSONDecodeError:
        parsed_content = None

    suggestions: list[str] = []

    if isinstance(parsed_content, dict):
        raw_suggestions = parsed_content.get("suggestions", [])
        if isinstance(raw_suggestions, list):
            suggestions = [str(item) for item in raw_suggestions if str(item).strip()]
    elif isinstance(parsed_content, list):
        suggestions = [str(item) for item in parsed_content if str(item).strip()]
    elif isinstance(parsed_content, str):
        suggestions = [parsed_content]

    if not suggestions:
        suggestions = [line.lstrip("-•0123456789. )").strip() for line in content.splitlines() if line.strip()]

    return _normalize_llm_suggestions(suggestions[:max_suggestions])


class LLMFeedbackService:
    def __init__(self, config: LLMFeedbackConfig):
        self.config = config
        self._cache: dict[str, dict[str, Any]] = self._load_cache()

    @classmethod
    def from_environment(cls) -> "LLMFeedbackService":
        api_key = os.getenv("RESUME_ANALYSER_LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        enabled = _env_flag("RESUME_ANALYSER_LLM_ENABLED", False)
        endpoint = os.getenv("RESUME_ANALYSER_LLM_ENDPOINT", DEFAULT_LLM_ENDPOINT).strip() or DEFAULT_LLM_ENDPOINT
        model = os.getenv("RESUME_ANALYSER_LLM_MODEL", DEFAULT_LLM_MODEL).strip() or DEFAULT_LLM_MODEL

        cache_path_value = os.getenv("RESUME_ANALYSER_LLM_CACHE_PATH")
        cache_path = Path(cache_path_value).expanduser().resolve() if cache_path_value else DEFAULT_LLM_CACHE_PATH

        timeout_seconds = float(os.getenv("RESUME_ANALYSER_LLM_TIMEOUT_SECONDS", "20"))
        max_suggestions = max(1, int(os.getenv("RESUME_ANALYSER_LLM_MAX_SUGGESTIONS", "4")))

        config = LLMFeedbackConfig(
            enabled=enabled and bool(api_key.strip()),
            api_key=api_key.strip(),
            endpoint=endpoint,
            model=model,
            cache_path=cache_path,
            timeout_seconds=timeout_seconds,
            max_suggestions=max_suggestions,
        )
        return cls(config)

    def is_enabled(self) -> bool:
        return self.config.enabled and bool(self.config.api_key)

    def _load_cache(self) -> dict[str, dict[str, Any]]:
        if not self.config.cache_path.exists():
            return {}

        try:
            with self.config.cache_path.open("r", encoding="utf-8") as handle:
                cached_data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}

        return cached_data if isinstance(cached_data, dict) else {}

    def _save_cache(self) -> None:
        try:
            self.config.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config.cache_path.open("w", encoding="utf-8") as handle:
                json.dump(self._cache, handle, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _request_feedback(self, resume_bullets: list[str], job_description_text: str) -> list[str]:
        bullet_text = "\n".join(f"{index + 1}. {bullet}" for index, bullet in enumerate(resume_bullets))
        payload = {
            "model": self.config.model,
            "temperature": 0.2,
            "max_tokens": 350,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a resume rewriting coach. Compare the resume bullets against the job description "
                        "and return JSON only with a suggestions array. Each suggestion should be concise, concrete, "
                        "and action-oriented. Focus on vague language, weak impact, missing metrics, and role-fit gaps."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Resume bullets:\n{bullet_text}\n\n"
                        f"Job description:\n{_truncate_text(job_description_text, 2200)}\n\n"
                        "Return JSON in this shape: {\"suggestions\": [\"...\"]}. Limit the list to the strongest edits."
                    ),
                },
            ],
        }

        request = urllib_request.Request(
            self.config.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ResumeAnalyser/1.0",
            },
            method="POST",
        )

        try:
            with urllib_request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (urllib_error.HTTPError, urllib_error.URLError, TimeoutError, ValueError):
            return []

        content = ""
        if isinstance(response_payload, dict):
            choices = response_payload.get("choices", [])
            if choices:
                message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
                if isinstance(message, dict):
                    content = str(message.get("content", ""))

            if not content:
                content = str(response_payload.get("content", ""))

        return _parse_llm_feedback_content(content, self.config.max_suggestions)

    def get_feedback(self, resume_text: str, job_description_text: str, config: Mapping[str, Any]) -> LLMFeedbackResult:
        if not self.is_enabled() or not resume_text.strip() or not job_description_text.strip():
            return LLMFeedbackResult(enabled=self.is_enabled(), model=self.config.model)

        action_verbs = list(config.get("action_verbs", []))
        resume_bullets = _extract_resume_bullets(resume_text, action_verbs)
        if not resume_bullets:
            return LLMFeedbackResult(enabled=self.is_enabled(), model=self.config.model)

        cache_key = _build_llm_cache_key(resume_bullets, job_description_text, self.config)
        cached_entry = self._cache.get(cache_key)
        if isinstance(cached_entry, dict):
            cached_suggestions = cached_entry.get("suggestions", [])
            if isinstance(cached_suggestions, list):
                return LLMFeedbackResult(
                    suggestions=_normalize_llm_suggestions([str(item) for item in cached_suggestions]),
                    cached=True,
                    enabled=True,
                    model=self.config.model,
                )

        suggestions = self._request_feedback(resume_bullets, job_description_text)
        if suggestions:
            self._cache[cache_key] = {
                "suggestions": suggestions,
                "model": self.config.model,
            }
            self._save_cache()

        return LLMFeedbackResult(
            suggestions=suggestions,
            cached=False,
            enabled=True,
            model=self.config.model,
            error_message=None if suggestions else "No AI feedback was returned",
        )


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
    except Exception:
        return None

    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


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


def _safe_semantic_similarity(resume_text: str, job_description_text: str) -> tuple[float | None, bool]:
    if not resume_text.strip() or not job_description_text.strip():
        return None, False

    model = _load_sentence_transformer_model()
    if model is None:
        return None, False

    try:
        embeddings = model.encode([resume_text, job_description_text], normalize_embeddings=True)
        similarity = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
        return similarity, True
    except Exception:
        return None, False


def _extract_skills_and_keywords(job_description_text: str, resume_text: str) -> tuple[list[str], list[str], list[str]]:
    """Smart keyword and skill extractor that prioritizes domain skills and technical terms over raw line text."""
    if not job_description_text.strip() or not resume_text.strip():
        return [], [], []

    lower_jd = job_description_text.lower()
    lower_resume = resume_text.lower()

    found_jd_skills: list[str] = []
    seen_skills: set[str] = set()

    # 1. Match against known industry skills taxonomy
    for skill in COMMON_INDUSTRY_SKILLS:
        # Check boundary match
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, lower_jd):
            # Clean skill title
            display_skill = " ".join(word.capitalize() if word not in {"aws", "sql", "api", "apis", "ci/cd", "cicd", "k8s", "nlp", "ui/ux", "seo", "tdd", "oop", "gcp", "r"} else word.upper() for word in skill.split())
            if display_skill.lower() not in seen_skills:
                seen_skills.add(display_skill.lower())
                found_jd_skills.append(display_skill)

    # 2. Dynamic high-value N-gram extraction from the Job Description
    cleaned_jd = _clean_text(job_description_text)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=35)
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_jd])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        sorted_indices = scores.argsort()[::-1]

        for idx in sorted_indices:
            term = feature_names[idx].strip()
            # Ignore numbers, single chars, or boilerplate filler
            if len(term) < 3 or term.isdigit() or term in BOILERPLATE_STOPWORDS:
                continue
            if any(stop in term.split() for stop in BOILERPLATE_STOPWORDS):
                continue
            
            display_term = " ".join(word.capitalize() for word in term.split())
            if display_term.lower() not in seen_skills:
                seen_skills.add(display_term.lower())
                found_jd_skills.append(display_term)
                
            if len(found_jd_skills) >= 15:
                break
    except Exception:
        pass

    # Ensure minimum skills list
    if not found_jd_skills:
        found_jd_skills = ["Technical Skills", "Communication", "Problem Solving", "Collaboration"]

    # 3. Match against Resume Text
    present_keywords: list[str] = []
    missing_keywords: list[str] = []

    for skill in found_jd_skills:
        # Flexible match: e.g. "REST APIs" matches "rest api", "restful", "rest"
        search_term = skill.lower()
        if search_term == "rest apis" or search_term == "rest api":
            pattern = r"\b(rest|restful|rest api|rest apis)\b"
        elif search_term == "ci/cd" or search_term == "cicd":
            pattern = r"\b(ci/cd|cicd|continuous integration|continuous deployment)\b"
        elif search_term == "kubernetes" or search_term == "k8s":
            pattern = r"\b(kubernetes|k8s)\b"
        elif search_term == "react" or search_term == "react.js":
            pattern = r"\b(react|reactjs|react\.js)\b"
        elif search_term == "node.js" or search_term == "node":
            pattern = r"\b(node|nodejs|node\.js)\b"
        elif search_term == "aws":
            pattern = r"\b(aws|amazon web services)\b"
        elif search_term == "gcp":
            pattern = r"\b(gcp|google cloud)\b"
        else:
            pattern = r"\b" + re.escape(search_term) + r"\b"

        if re.search(pattern, lower_resume):
            present_keywords.append(skill)
        else:
            missing_keywords.append(skill)

    return found_jd_skills, present_keywords, missing_keywords


def _detect_sections_with_regex(resume_text: str, config: Mapping[str, Any]) -> dict[str, bool]:
    section_patterns = _compile_patterns(config)
    return {section_name: bool(pattern.search(resume_text)) for section_name, pattern in section_patterns.items()}


def _detect_sections_with_spacy(resume_text: str, config: Mapping[str, Any]) -> dict[str, bool] | None:
    nlp = _load_spacy_nlp()
    if nlp is None:
        return None

    sections = _detect_sections_with_regex(resume_text, config)
    doc = nlp(resume_text)
    entity_labels = {ent.label_.upper() for ent in getattr(doc, "ents", [])}
    cleaned_resume = _clean_text(resume_text)
    lower_resume = resume_text.lower()

    section_headers = config.get("section_headers", {})
    education_keywords = section_headers.get("Education", [])
    experience_keywords = section_headers.get("Experience", [])
    contact_keywords = section_headers.get("Contact Info", [])
    skills_keywords = section_headers.get("Skills", [])
    action_verbs = config.get("action_verbs", [])

    if not sections.get("Contact Info"):
        email_like = re.search(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", resume_text)
        phone_like = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", resume_text)
        sections["Contact Info"] = bool(email_like or phone_like or any(keyword in lower_resume for keyword in contact_keywords))

    if not sections.get("Education"):
        education_signal = any(keyword in lower_resume for keyword in education_keywords) or bool(
            re.search(r"\b(bsc|msc|phd|ba|bs|associate|bachelor|master|degree|university|college)\b", lower_resume)
        )
        sections["Education"] = bool(education_signal)

    if not sections.get("Experience"):
        experience_signal = any(keyword in lower_resume for keyword in experience_keywords) or any(
            verb in cleaned_resume for verb in action_verbs
        )
        sections["Experience"] = bool(experience_signal)

    if not sections.get("Skills"):
        sections["Skills"] = bool(any(keyword in cleaned_resume for keyword in skills_keywords))

    return sections


def _detect_sections(resume_text: str, config: Mapping[str, Any]) -> dict[str, bool]:
    spacy_sections = _detect_sections_with_spacy(resume_text, config)
    if spacy_sections is not None:
        return spacy_sections

    return _detect_sections_with_regex(resume_text, config)


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

    if missing_keywords:
        top_missing = ", ".join(missing_keywords[:3])
        suggestions.append(f"Add key target skills naturally into your experience: {top_missing}.")

    if len(action_verbs) < 4:
        suggestions.append("Strengthen your bullet points using action verbs like 'Architected', 'Spearheaded', 'Optimized', or 'Engineered'.")

    if quantifiable_metrics < 2:
        suggestions.append("Quantify your achievements with measurable results (e.g., 'Reduced query latency by 35%').")

    if word_count > 800:
        suggestions.append("Your resume is slightly lengthy. Aim for a concise, high-impact 1-2 page structure.")
    elif word_count < 250:
        suggestions.append("Your resume seems short. Elaborate on project deliverables, responsibilities, and technical tools.")

    for section_name, present in sections.items():
        if not present:
            suggestions.append(f"Add a distinct '{section_name}' section header to ensure ATS parsers classify your credentials accurately.")

    if not suggestions:
        suggestions.append("Your resume is well-tailored. Keep impact metrics and strongest technical achievements near the top.")

    return suggestions


def calculate_ats_match_score(
    present_keywords: list[str],
    jd_keywords: list[str],
    raw_tfidf_similarity: float,
    sections: Mapping[str, bool],
    action_verbs: list[str],
    quantifiable_metrics: int,
) -> float:
    """
    Industry-grade ATS match score algorithm:
    - 60% Skill & Role Keyword Coverage (matching specific skills, not whole text boilerplate)
    - 25% Domain Context / Normalized Relevance (scales non-linear text relevance appropriately)
    - 15% ATS Health (Section detection, Action Verbs, Metrics)
    """
    # 1. Skill Match Ratio (0.0 to 1.0)
    if jd_keywords:
        skills_ratio = len(present_keywords) / len(jd_keywords)
    else:
        skills_ratio = 0.85

    # 2. Scaled Text Relevance (maps 0.15 - 0.45 typical raw cosine to realistic 0.60 - 0.95 range)
    if raw_tfidf_similarity > 0:
        scaled_relevance = min(1.0, math.sqrt(raw_tfidf_similarity) * 1.35)
    else:
        scaled_relevance = 0.40

    # 3. Structure & Health Ratio
    section_count = sum(1 for present in sections.values() if present)
    section_ratio = section_count / max(1, len(sections)) if sections else 1.0
    verb_ratio = min(1.0, len(action_verbs) / 4)
    metric_bonus = 0.1 if quantifiable_metrics > 0 else 0.0
    health_ratio = min(1.0, (section_ratio * 0.7) + (verb_ratio * 0.2) + metric_bonus)

    # 4. Weighted Composite Score
    # Tailored resumes with high skill overlap score realistically in the 75% - 95%+ range
    final_score = (skills_ratio * 0.60) + (scaled_relevance * 0.25) + (health_ratio * 0.15)
    
    # Floor and ceiling boundaries
    final_score = max(0.10, min(0.98, final_score))
    return round(final_score, 3)


def analyze_resume(
    resume_text: str,
    job_description_text: str,
    config: Mapping[str, Any],
    similarity_mode: str = "tfidf",
) -> ResumeAnalysisResult:
    normalized_mode = similarity_mode.lower().strip()
    if normalized_mode not in {"tfidf", "semantic"}:
        normalized_mode = "tfidf"

    if not resume_text or not job_description_text:
        return ResumeAnalysisResult(
            similarity_mode=normalized_mode,
            similarity_score=0.0,
            word_count=0,
            readability=0.0,
            tfidf_similarity_score=0.0,
            semantic_similarity_score=None,
            semantic_similarity_available=False,
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

    raw_tfidf_similarity = _safe_similarity(cleaned_resume, cleaned_jd)
    semantic_similarity_score, semantic_similarity_available = _safe_semantic_similarity(resume_text, job_description_text)

    jd_keywords, present_keywords, missing_keywords = _extract_skills_and_keywords(job_description_text, resume_text)
    sections = _detect_sections(resume_text, config)
    action_verbs = _count_action_verbs(cleaned_resume, config)
    quantifiable_metrics = _count_quantifiable_metrics(resume_text)

    # Calculate ATS Match Score using industry-standard multi-factor formula
    similarity_score = calculate_ats_match_score(
        present_keywords=present_keywords,
        jd_keywords=jd_keywords,
        raw_tfidf_similarity=raw_tfidf_similarity,
        sections=sections,
        action_verbs=action_verbs,
        quantifiable_metrics=quantifiable_metrics,
    )

    suggestions = _build_suggestions(
        similarity_score,
        missing_keywords,
        action_verbs,
        quantifiable_metrics,
        word_count,
        sections,
    )

    return ResumeAnalysisResult(
        similarity_mode=normalized_mode,
        similarity_score=similarity_score,
        tfidf_similarity_score=raw_tfidf_similarity,
        semantic_similarity_score=semantic_similarity_score,
        semantic_similarity_available=semantic_similarity_available,
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
        self.similarity_mode = "tfidf"
        self.results = ResumeAnalysisResult(similarity_score=0.0, word_count=0, readability=0.0)
        self.job_roles = self.config.get("job_roles", {})
        self.feedback_service = LLMFeedbackService.from_environment()

    def load_resume(self, file_path: str | os.PathLike[str]) -> str:
        self.resume_text = load_resume_text(file_path)
        return self.resume_text

    def set_job_description(self, text: str) -> None:
        self.job_description = text

    def set_similarity_mode(self, mode: str) -> None:
        normalized_mode = mode.lower().strip()
        self.similarity_mode = normalized_mode if normalized_mode in {"tfidf", "semantic"} else "tfidf"

    def analyze(self) -> dict[str, Any]:
        self.results = analyze_resume(
            self.resume_text,
            self.job_description,
            self.config,
            similarity_mode=self.similarity_mode,
        )
        feedback_result = self.feedback_service.get_feedback(self.resume_text, self.job_description, self.config)
        self.results.llm_feedback = feedback_result.suggestions
        self.results.llm_feedback_enabled = feedback_result.enabled
        self.results.llm_feedback_cached = feedback_result.cached
        self.results.llm_feedback_error = feedback_result.error_message
        self.results.llm_feedback_model = feedback_result.model
        return asdict(self.results)

    def generate_recommendations(self, similarity, missing_keywords, sections):
        self.analyze()
        return self.results.suggestions + self.results.llm_feedback