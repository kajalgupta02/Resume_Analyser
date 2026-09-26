"""Domain models returned by resume analysis services."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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
    endpoint: str = "https://api.openai.com/v1/chat/completions"
    model: str = "gpt-4o-mini"
    cache_path: Path = Path(__file__).resolve().parents[2] / "resume_llm_feedback_cache.json"
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
