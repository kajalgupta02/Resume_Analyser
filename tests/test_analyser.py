import json
from pathlib import Path

import pytest

from app.logic.analyser import (
    ResumeAnalysisResult,
    ResumeAnalyser,
    analyze_resume,
    load_analysis_config,
    load_resume_text,
)


@pytest.fixture(scope="module")
def analysis_config():
    return load_analysis_config()


@pytest.fixture()
def analyser():
    return ResumeAnalyser()


def test_section_detection_missing_sections(analysis_config):
    resume_text = "Jane Doe\nEmail: jane@example.com\nSkills: Python, SQL\n"
    result = analyze_resume(resume_text, "Looking for data analysis and dashboards", analysis_config)

    assert isinstance(result, ResumeAnalysisResult)
    assert result.sections["Contact Info"] is True
    assert result.sections["Education"] is False
    assert result.sections["Experience"] is False
    assert result.sections["Skills"] is True


def test_section_detection_malformed_sections(analysis_config):
    resume_text = "EDUCATION: BSc Computer Science\nEXPERIENCE- Built APIs\nSKILLS: Python\n"
    result = analyze_resume(resume_text, "python api development", analysis_config)

    assert result.sections["Education"] is True
    assert result.sections["Experience"] is True
    assert result.sections["Skills"] is True


@pytest.mark.parametrize(
    "resume_text, job_description, expected_min, expected_max",
    [
        (
            "Data Analyst with Python, SQL, Excel, Tableau, and dashboards. Improved reporting and built metrics.",
            "Need python sql excel tableau reporting and dashboards",
            0.45,
            1.0,
        ),
        (
            "Frontend developer skilled in React, TypeScript, HTML, CSS, and responsive design.",
            "Looking for React TypeScript frontend developer",
            0.35,
            1.0,
        ),
        (
            "Ops engineer with Docker, Kubernetes, Terraform, AWS, and CI/CD automation.",
            "Seeking DevOps engineer with Kubernetes and AWS",
            0.25,
            1.0,
        ),
    ],
)
def test_scoring_ranges_known_pairs(analysis_config, resume_text, job_description, expected_min, expected_max):
    result = analyze_resume(resume_text, job_description, analysis_config)

    assert expected_min <= result.similarity_score <= expected_max
    assert result.word_count > 0
    assert result.readability >= 0
    assert result.readability <= 100


def test_keyword_extraction_edge_cases(analysis_config):
    result = analyze_resume("", "python python python", analysis_config)

    assert result.word_count == 0
    assert result.jd_keywords == []
    assert result.present_keywords == []
    assert result.missing_keywords == []


@pytest.mark.parametrize(
    "file_name, content, expected_exception",
    [
        ("empty.txt", "", None),
        ("corrupted.pdf", b"%PDF-1.4 corrupted data", Exception),
    ],
)
def test_file_parsing_edge_cases(tmp_path, file_name, content, expected_exception):
    file_path = tmp_path / file_name
    if isinstance(content, bytes):
        file_path.write_bytes(content)
    else:
        file_path.write_text(content, encoding="utf-8")

    if expected_exception is None:
        assert load_resume_text(str(file_path)) == ""
    else:
        with pytest.raises(expected_exception):
            load_resume_text(str(file_path))


def test_file_parsing_docx_and_non_english(tmp_path):
    docx_path = tmp_path / "sample.docx"
    # Create a minimal DOCX archive using the python-docx library when available.
    from docx import Document

    document = Document()
    document.add_paragraph("Résumé avec expérience en analyse de données")
    document.save(str(docx_path))

    parsed = load_resume_text(str(docx_path))
    assert "analyse" in parsed.lower()

    txt_path = tmp_path / "non_english.txt"
    txt_path.write_text("Experiencia en análisis de datos y Python", encoding="utf-8")
    parsed_txt = load_resume_text(str(txt_path))
    assert "análisis" in parsed_txt.lower()
