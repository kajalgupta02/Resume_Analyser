from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResumeAnalysisResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    similarity_score: float = Field(..., ge=0, le=1, description="Primary match score between the resume and job description.")
    word_count: int = Field(..., ge=0, description="Total number of words in the uploaded resume.")
    readability: float = Field(..., ge=0, le=100, description="Readability score on a 0-100 scale.")
    similarity_mode: str = Field(default="tfidf", description="Similarity mode used for the primary score.")
    tfidf_similarity_score: float = Field(..., ge=0, le=1, description="TF-IDF similarity score.")
    semantic_similarity_score: float | None = Field(default=None, ge=0, le=1, description="Semantic similarity score when available.")
    semantic_similarity_available: bool = Field(..., description="Whether semantic similarity was available for the run.")
    jd_keywords: list[str] = Field(default_factory=list, description="Keywords extracted from the job description.")
    present_keywords: list[str] = Field(default_factory=list, description="Keywords found in the resume.")
    missing_keywords: list[str] = Field(default_factory=list, description="Keywords missing from the resume.")
    action_verbs: list[str] = Field(default_factory=list, description="Action verbs detected in the resume.")
    quantifiable_metrics: int = Field(..., ge=0, description="Count of measurable metrics found in the resume.")
    sections: dict[str, bool] = Field(default_factory=dict, description="Detected ATS resume sections.")
    suggestions: list[str] = Field(default_factory=list, description="Deterministic improvement suggestions.")
    llm_feedback: list[str] = Field(default_factory=list, description="Optional AI feedback suggestions.")
    llm_feedback_enabled: bool = Field(..., description="Whether LLM feedback was enabled.")
    llm_feedback_cached: bool = Field(..., description="Whether the AI feedback came from cache.")
    llm_feedback_error: str | None = Field(default=None, description="AI feedback error message, if any.")
    llm_feedback_model: str | None = Field(default=None, description="Model used for AI feedback, if any.")


class AnalysisReportSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique report identifier.")
    date: str = Field(..., description="Timestamp for when the report was created.")
    results: ResumeAnalysisResultSchema


class AnalyzeResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: AnalysisReportSchema


class HistoryListResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reports: list[AnalysisReportSchema]


class ErrorResponseSchema(BaseModel):
    detail: str
    extra: dict[str, Any] | None = None