from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from ..logic.analyser import DEFAULT_CONFIG_PATH, analyze_resume, load_analysis_config, load_resume_text
from ..logic.history_manager import DEFAULT_HISTORY_FILE, HistoryManager


class ResumeAnalysisService:
    def __init__(self, config_path: str | Path | None = None, history_file: str | Path | None = None):
        self.config = load_analysis_config(config_path or DEFAULT_CONFIG_PATH)
        self.history_manager = HistoryManager(history_file=history_file or DEFAULT_HISTORY_FILE)

    def analyze_upload(
        self,
        resume_filename: str,
        resume_content: bytes,
        job_description: str,
        similarity_mode: str = "tfidf",
    ) -> dict[str, Any]:
        suffix = Path(resume_filename).suffix or ".txt"
        temp_path: Path | None = None

        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(resume_content)
            temp_path = Path(temp_file.name)

        try:
            resume_text = load_resume_text(temp_path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

        analysis = analyze_resume(resume_text, job_description, self.config, similarity_mode=similarity_mode)
        report = self.history_manager.add_analysis(asdict(analysis))
        return report

    def get_report(self, report_id: str):
        return self.history_manager.get_analysis_by_id(report_id)

    def list_history(self):
        return self.history_manager.get_history()