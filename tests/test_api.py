from fastapi.testclient import TestClient

import app.logic.history_manager as history_manager_module
from app.api.main import create_app
from app.api.service import ResumeAnalysisService


def test_upload_analyze_and_fetch_history(tmp_path, monkeypatch):
    monkeypatch.setattr(history_manager_module, "LEGACY_HISTORY_JSON", tmp_path / "missing.json")
    service = ResumeAnalysisService(history_file=tmp_path / "history.json")
    client = TestClient(create_app(service=service))

    response = client.post(
        "/analyze",
        data={
            "job_description": "Looking for Python SQL dashboards and reporting experience",
            "similarity_mode": "tfidf",
        },
        files={
            "resume": (
                "resume.txt",
                b"Data analyst with Python, SQL, dashboards, and reporting wins.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    report = payload["report"]

    assert report["id"]
    assert report["results"]["word_count"] > 0
    assert report["results"]["sections"]

    report_id = report["id"]

    fetched = client.get(f"/reports/{report_id}")
    assert fetched.status_code == 200
    assert fetched.json()["report"]["id"] == report_id

    history = client.get("/history")
    assert history.status_code == 200
    assert len(history.json()["reports"]) == 1


def test_missing_report_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(history_manager_module, "LEGACY_HISTORY_JSON", tmp_path / "missing.json")
    service = ResumeAnalysisService(history_file=tmp_path / "history.json")
    client = TestClient(create_app(service=service))

    response = client.get("/reports/missing-report-id")

    assert response.status_code == 404