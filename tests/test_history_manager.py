from app.logic.history_manager import HistoryManager


def test_history_manager_persists_entries_in_sqlite(tmp_path, monkeypatch):
    db_path = tmp_path / "resume_analysis.db"
    monkeypatch.setattr("app.logic.history_manager.LEGACY_HISTORY_JSON", tmp_path / "missing.json")

    manager = HistoryManager(history_file=db_path)
    entry = manager.add_analysis(
        {
            "similarity_score": 0.82,
            "word_count": 210,
            "readability": 63.5,
            "similarity_mode": "tfidf",
            "tfidf_similarity_score": 0.82,
            "semantic_similarity_score": None,
            "semantic_similarity_available": False,
            "jd_keywords": ["python"],
            "present_keywords": ["python"],
            "missing_keywords": [],
            "action_verbs": ["developed"],
            "quantifiable_metrics": 2,
            "sections": {"Skills": True},
            "suggestions": ["Add more measurable outcomes."],
            "llm_feedback": [],
            "llm_feedback_enabled": False,
            "llm_feedback_cached": False,
            "llm_feedback_error": None,
            "llm_feedback_model": None,
        }
    )

    assert entry is not None
    assert entry["id"]

    reloaded = HistoryManager(history_file=db_path)
    history = reloaded.get_history()

    assert len(history) == 1
    assert history[0]["id"] == entry["id"]
    assert history[0]["results"]["similarity_score"] == 0.82


def test_legacy_json_history_is_imported_once(tmp_path, monkeypatch):
    legacy_json = tmp_path / "resume_analysis_history.json"
    legacy_json.write_text(
        """
        [
          {
            "id": "legacy-report-1",
            "date": "2026-05-26 00:13:40",
            "results": {
              "similarity_score": 0.28,
              "word_count": 394,
              "readability": 15.7,
              "similarity_mode": "tfidf",
              "tfidf_similarity_score": 0.28,
              "semantic_similarity_score": null,
              "semantic_similarity_available": false,
              "jd_keywords": ["python"],
              "present_keywords": ["python"],
              "missing_keywords": [],
              "action_verbs": [],
              "quantifiable_metrics": 12,
              "sections": {"Skills": true},
              "suggestions": [],
              "llm_feedback": [],
              "llm_feedback_enabled": false,
              "llm_feedback_cached": false,
              "llm_feedback_error": null,
              "llm_feedback_model": null
            }
          }
        ]
        """.strip(),
        encoding="utf-8",
    )

    db_path = tmp_path / "resume_analysis.db"
    monkeypatch.setattr("app.logic.history_manager.LEGACY_HISTORY_JSON", legacy_json)

    manager = HistoryManager(history_file=db_path)

    history = manager.get_history()
    assert len(history) == 1
    assert history[0]["id"] == "legacy-report-1"
    assert history[0]["results"]["word_count"] == 394

    second_manager = HistoryManager(history_file=db_path)
    assert len(second_manager.get_history()) == 1
