from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


DEFAULT_HISTORY_FILE = Path(__file__).resolve().parents[3] / "resume_analysis.db"
LEGACY_HISTORY_JSON = Path(__file__).resolve().parents[3] / "resume_analysis_history.json"


class HistoryManager:
    def __init__(self, history_file: str | Path = DEFAULT_HISTORY_FILE):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
        self._migrate_legacy_json_history()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.history_file)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_database(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS resumes (
                    id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                    filename TEXT,
                    file_type TEXT,
                    content_hash TEXT UNIQUE,
                    extracted_text TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    resume_id TEXT REFERENCES resumes(id) ON DELETE SET NULL,
                    job_description TEXT,
                    similarity_mode TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL UNIQUE REFERENCES analyses(id) ON DELETE CASCADE,
                    created_at TEXT NOT NULL,
                    results_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def _has_metadata_flag(self, key: str) -> bool:
        with closing(self._connect()) as connection:
            row = connection.execute("SELECT 1 FROM metadata WHERE key = ?", (key,)).fetchone()
            return row is not None

    def _set_metadata_flag(self, key: str, value: str) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO metadata(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def _normalize_results(self, results: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "similarity_score": float(results.get("similarity_score", 0.0) or 0.0),
            "word_count": int(results.get("word_count", 0) or 0),
            "readability": float(results.get("readability", 0.0) or 0.0),
            "similarity_mode": str(results.get("similarity_mode", "tfidf") or "tfidf"),
            "tfidf_similarity_score": float(results.get("tfidf_similarity_score", results.get("similarity_score", 0.0)) or 0.0),
            "semantic_similarity_score": results.get("semantic_similarity_score"),
            "semantic_similarity_available": bool(results.get("semantic_similarity_available", False)),
            "jd_keywords": list(results.get("jd_keywords", []) or []),
            "present_keywords": list(results.get("present_keywords", []) or []),
            "missing_keywords": list(results.get("missing_keywords", []) or []),
            "action_verbs": list(results.get("action_verbs", []) or []),
            "quantifiable_metrics": int(results.get("quantifiable_metrics", 0) or 0),
            "sections": dict(results.get("sections", {}) or {}),
            "suggestions": list(results.get("suggestions", []) or []),
            "llm_feedback": list(results.get("llm_feedback", []) or []),
            "llm_feedback_enabled": bool(results.get("llm_feedback_enabled", False)),
            "llm_feedback_cached": bool(results.get("llm_feedback_cached", False)),
            "llm_feedback_error": results.get("llm_feedback_error"),
            "llm_feedback_model": results.get("llm_feedback_model"),
        }
        return normalized

    def _migrate_legacy_json_history(self) -> None:
        if self._has_metadata_flag("legacy_json_history_imported"):
            return

        if not LEGACY_HISTORY_JSON.exists():
            self._set_metadata_flag("legacy_json_history_imported", "true")
            return

        try:
            with LEGACY_HISTORY_JSON.open("r", encoding="utf-8") as handle:
                legacy_history = json.load(handle)
        except (OSError, json.JSONDecodeError):
            self._set_metadata_flag("legacy_json_history_imported", "true")
            return

        if not isinstance(legacy_history, list) or not legacy_history:
            self._set_metadata_flag("legacy_json_history_imported", "true")
            return

        with closing(self._connect()) as connection, connection:
            existing_count = connection.execute("SELECT COUNT(*) AS count FROM reports").fetchone()["count"]
            if existing_count:
                self._set_metadata_flag("legacy_json_history_imported", "true")
                return

            for entry in legacy_history:
                if not isinstance(entry, dict):
                    continue

                report_id = str(entry.get("id") or uuid4().hex)
                created_at = str(entry.get("date") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                results = entry.get("results") or {}
                if not isinstance(results, dict):
                    continue

                normalized_results = self._normalize_results(results)

                resume_id = uuid4().hex
                results_json = json.dumps(normalized_results, ensure_ascii=False)

                connection.execute(
                    "INSERT OR IGNORE INTO resumes(id, filename, file_type, extracted_text) VALUES(?, ?, ?, ?)",
                    (resume_id, None, None, None),
                )
                connection.execute(
                    """
                    INSERT OR REPLACE INTO analyses(id, resume_id, job_description, similarity_mode, results_json, created_at)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        report_id,
                        resume_id,
                        None,
                        str(normalized_results.get("similarity_mode") or "tfidf"),
                        results_json,
                        created_at,
                    ),
                )
                connection.execute(
                    """
                    INSERT OR REPLACE INTO reports(id, analysis_id, created_at, results_json)
                    VALUES(?, ?, ?, ?)
                    """,
                    (report_id, report_id, created_at, results_json),
                )

        self._set_metadata_flag("legacy_json_history_imported", "true")

    def _row_to_entry(self, row: sqlite3.Row) -> dict[str, Any]:
        results = json.loads(row["results_json"])
        return {
            "id": row["id"],
            "date": row["created_at"],
            "results": self._normalize_results(results if isinstance(results, dict) else {}),
        }

    def add_analysis(self, analysis_result: dict[str, Any]):
        if not analysis_result:
            return None

        report_id = uuid4().hex
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        normalized_results = self._normalize_results(analysis_result)
        results_json = json.dumps(normalized_results, ensure_ascii=False)
        resume_id = uuid4().hex

        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO resumes(id, filename, file_type, extracted_text) VALUES(?, ?, ?, ?)",
                (resume_id, None, None, None),
            )
            connection.execute(
                """
                INSERT INTO analyses(id, resume_id, job_description, similarity_mode, results_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    resume_id,
                    None,
                    str(normalized_results.get("similarity_mode") or "tfidf"),
                    results_json,
                    created_at,
                ),
            )
            connection.execute(
                """
                INSERT INTO reports(id, analysis_id, created_at, results_json)
                VALUES(?, ?, ?, ?)
                """,
                (report_id, report_id, created_at, results_json),
            )

        return {
            "id": report_id,
            "date": created_at,
            "results": normalized_results,
        }

    def get_history(self):
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, created_at, results_json FROM reports ORDER BY created_at DESC, rowid DESC"
            ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def get_analysis_by_id(self, entry_id):
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT id, created_at, results_json FROM reports WHERE id = ?",
                (entry_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_entry(row)
