"""Optional OpenAI-compatible feedback adapter with a local response cache."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping
from urllib import error as urllib_error
from urllib import request as urllib_request

from .constants import DEFAULT_LLM_ENDPOINT, DEFAULT_LLM_MODEL
from .models import LLMFeedbackConfig, LLMFeedbackResult

DEFAULT_LLM_CACHE_PATH = Path(__file__).resolve().parents[2] / "resume_llm_feedback_cache.json"


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def _truncate_text(text: str, limit: int = 900) -> str:
    return text.strip() if len(text.strip()) <= limit else text.strip()[: limit - 3].rstrip() + "..."


def _normalize_suggestions(suggestions: list[str]) -> list[str]:
    cleaned, seen = [], set()
    for suggestion in suggestions:
        item = suggestion.strip()
        if item and item not in seen:
            seen.add(item); cleaned.append(item)
    return cleaned


def _extract_resume_bullets(resume_text: str, action_verbs: list[str], limit: int = 8) -> list[str]:
    bullets = []
    for line in resume_text.splitlines():
        line = line.strip()
        match = re.match(r"^\s*(?:[-*•]|\d+[.)])\s+(.*)$", line)
        candidate = match.group(1).strip() if match else (line if len(line.split()) >= 6 and any(verb in line.lower() for verb in action_verbs) else "")
        if candidate and candidate not in bullets:
            bullets.append(candidate)
        if len(bullets) >= limit:
            return bullets
    return bullets or [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", resume_text) if sentence.strip()][:limit]


def _parse_content(content: str, maximum: int) -> list[str]:
    try:
        parsed = json.loads(content.strip()) if content.strip() else None
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict): raw = parsed.get("suggestions", [])
    elif isinstance(parsed, list): raw = parsed
    elif isinstance(parsed, str): raw = [parsed]
    else: raw = [line.lstrip("-•0123456789. )").strip() for line in content.splitlines() if line.strip()]
    return _normalize_suggestions([str(item) for item in raw])[:maximum]


class LLMFeedbackService:
    def __init__(self, config: LLMFeedbackConfig):
        self.config = config
        self._cache = self._load_cache()

    @classmethod
    def from_environment(cls) -> "LLMFeedbackService":
        api_key = (os.getenv("RESUME_ANALYSER_LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
        cache_value = os.getenv("RESUME_ANALYSER_LLM_CACHE_PATH")
        config = LLMFeedbackConfig(enabled=_env_flag("RESUME_ANALYSER_LLM_ENABLED") and bool(api_key), api_key=api_key, endpoint=os.getenv("RESUME_ANALYSER_LLM_ENDPOINT", DEFAULT_LLM_ENDPOINT).strip() or DEFAULT_LLM_ENDPOINT, model=os.getenv("RESUME_ANALYSER_LLM_MODEL", DEFAULT_LLM_MODEL).strip() or DEFAULT_LLM_MODEL, cache_path=Path(cache_value).expanduser().resolve() if cache_value else DEFAULT_LLM_CACHE_PATH, timeout_seconds=float(os.getenv("RESUME_ANALYSER_LLM_TIMEOUT_SECONDS", "20")), max_suggestions=max(1, int(os.getenv("RESUME_ANALYSER_LLM_MAX_SUGGESTIONS", "4"))))
        return cls(config)

    def is_enabled(self) -> bool:
        return self.config.enabled and bool(self.config.api_key)

    def _load_cache(self) -> dict[str, dict[str, Any]]:
        try:
            with self.config.cache_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_cache(self) -> None:
        try:
            self.config.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config.cache_path.open("w", encoding="utf-8") as handle:
                json.dump(self._cache, handle, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _request_feedback(self, bullets: list[str], job_description: str) -> list[str]:
        bullet_text = "\n".join(f"{index + 1}. {bullet}" for index, bullet in enumerate(bullets))
        payload = {"model": self.config.model, "temperature": .2, "max_tokens": 350, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "You are a resume rewriting coach. Compare the resume bullets against the job description and return JSON only with a suggestions array. Each suggestion should be concise, concrete, and action-oriented. Focus on vague language, weak impact, missing metrics, and role-fit gaps."}, {"role": "user", "content": f"Resume bullets:\n{bullet_text}\n\nJob description:\n{_truncate_text(job_description, 2200)}\n\nReturn JSON in this shape: {{\"suggestions\": [\"...\"]}}. Limit the list to the strongest edits."}]}
        request = urllib_request.Request(self.config.endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "ResumeAnalyser/1.0"}, method="POST")
        try:
            with urllib_request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (urllib_error.HTTPError, urllib_error.URLError, TimeoutError, ValueError):
            return []
        choices = response_payload.get("choices", []) if isinstance(response_payload, dict) else []
        message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
        content = str(message.get("content", "")) if isinstance(message, dict) else ""
        return _parse_content(content or str(response_payload.get("content", "")), self.config.max_suggestions) if isinstance(response_payload, dict) else []

    def get_feedback(self, resume_text: str, job_description_text: str, config: Mapping[str, Any]) -> LLMFeedbackResult:
        if not self.is_enabled() or not resume_text.strip() or not job_description_text.strip():
            return LLMFeedbackResult(enabled=self.is_enabled(), model=self.config.model)
        bullets = _extract_resume_bullets(resume_text, list(config.get("action_verbs", [])))
        if not bullets:
            return LLMFeedbackResult(enabled=True, model=self.config.model)
        key_data = {"endpoint": self.config.endpoint, "model": self.config.model, "prompt_version": self.config.prompt_version, "resume_bullets": bullets, "job_description_text": job_description_text, "max_suggestions": self.config.max_suggestions}
        key = hashlib.sha256(json.dumps(key_data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        cached = self._cache.get(key, {})
        if isinstance(cached, dict) and isinstance(cached.get("suggestions"), list):
            return LLMFeedbackResult(suggestions=_normalize_suggestions([str(item) for item in cached["suggestions"]]), cached=True, enabled=True, model=self.config.model)
        suggestions = self._request_feedback(bullets, job_description_text)
        if suggestions:
            self._cache[key] = {"suggestions": suggestions, "model": self.config.model}; self._save_cache()
        return LLMFeedbackResult(suggestions=suggestions, enabled=True, model=self.config.model, error_message=None if suggestions else "No AI feedback was returned")
