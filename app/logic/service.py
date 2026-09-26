"""Application service coordinating analysis and optional LLM feedback."""

from __future__ import annotations

from dataclasses import asdict
import os
from typing import Any

from .analysis_engine import analyze_resume
from .config import load_analysis_config
from .llm_feedback import LLMFeedbackService
from .models import ResumeAnalysisResult
from .resume_reader import load_resume_text


class ResumeAnalyser:
    """Backward-compatible facade used by the UI."""

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
        self.similarity_mode = mode.lower().strip() if mode.lower().strip() in {"tfidf", "semantic"} else "tfidf"

    def analyze(self) -> dict[str, Any]:
        self.results = analyze_resume(self.resume_text, self.job_description, self.config, self.similarity_mode)
        feedback = self.feedback_service.get_feedback(self.resume_text, self.job_description, self.config)
        self.results.llm_feedback, self.results.llm_feedback_enabled = feedback.suggestions, feedback.enabled
        self.results.llm_feedback_cached, self.results.llm_feedback_error = feedback.cached, feedback.error_message
        self.results.llm_feedback_model = feedback.model
        return asdict(self.results)

    def generate_recommendations(self, similarity, missing_keywords, sections):
        self.analyze()
        return self.results.suggestions + self.results.llm_feedback
