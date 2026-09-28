"""
Unit Tests for ResumeService Business Coordinator.
"""

import pytest
from pathlib import Path
from app.database.connection import DatabaseConnection
from app.database.repository import ResumeRepository
from app.services.resume_service import ResumeService


@pytest.fixture
def temp_service(tmp_path):
    db_file = tmp_path / "test_service.db"
    repo = ResumeRepository(DatabaseConnection(db_file))
    return ResumeService(repository=repo)


def test_resume_service_crud_lifecycle(temp_service):
    # 1. Create
    resume = temp_service.create_resume(title="Product Manager")
    assert resume.id is not None
    assert resume.title == "Product Manager"

    # 2. Update
    resume.personal_info.full_name = "Dave Manager"
    updated = temp_service.update_resume(resume)
    assert updated.personal_info.full_name == "Dave Manager"

    # 3. Read All & Search
    all_resumes = temp_service.get_all_resumes()
    assert len(all_resumes) == 1
    
    searched = temp_service.search_resumes("Dave")
    assert len(searched) == 1

    # 4. Duplicate
    dup = temp_service.duplicate_resume(resume.id, "Product Manager Copy")
    assert dup.title == "Product Manager Copy"

    # 5. Delete
    assert temp_service.delete_resume(dup.id)
    assert len(temp_service.get_all_resumes()) == 1


def test_build_new_resume_from_jd(temp_service):
    base_text = """John Doe
    Email: john@example.com
    Phone: +1-555-0199
    Experienced Engineer specializing in Python."""

    jd_text = """Lead Python Cloud Architect
    Looking for a Lead Python Cloud Architect skilled in AWS, Docker, REST APIs, and System Design."""

    tailored_resume, jd_result = temp_service.build_new_resume_from_jd(base_text, jd_text)

    assert tailored_resume.id is not None
    assert "Tailored" in tailored_resume.title
    assert tailored_resume.personal_info.email == "john@example.com"
    assert jd_result.score > 0
    assert len(tailored_resume.skills) > 0


def test_pdf_resume_import(temp_service, tmp_path):
    # Generate sample PDF resume
    sample = temp_service.create_resume(title="PDF Import Sample")
    sample.personal_info.full_name = "Samantha Miller"
    sample.personal_info.email = "samantha@example.com"
    sample.personal_info.phone = "+1-555-0177"
    temp_service.update_resume(sample)

    target_pdf = tmp_path / "sample_import.pdf"
    temp_service.export_pdf(sample, target_path=target_pdf)

    # Import PDF back
    imported = temp_service.import_resume(target_pdf)
    assert imported.personal_info.full_name == "Samantha Miller"
    assert imported.personal_info.email == "samantha@example.com"


def test_ai_extension_hooks(temp_service):
    resume = temp_service.create_resume(title="AI Test")
    improved = temp_service.ai_improve_bullet("Developed microservices backend.")
    assert improved == "Developed microservices backend."

    summary = temp_service.ai_generate_summary(resume)
    assert "Results-driven" in summary

    match = temp_service.ai_match_job_description(resume, "Required: Python, SQL")
    assert match["match_percentage"] > 0


def test_full_resume_import_and_jd_tailoring(temp_service):
    base_text = """Nandini Ande
andenandini183@gmail.com | 7995970147

SUMMARY
Motivated student specializing in Artificial Intelligence and Machine Learning.

WORK EXPERIENCE
AI Developer Intern — Tech Startup
- Built machine learning models for natural language processing using Python.
- Designed API endpoints using FastAPI.

EDUCATION
B.Tech in AI & ML — State University
2022 - 2026

PROJECTS
Smart Resume Builder — Python, Flask, SQLite
- Created an ATS analyzer and resume generator app.

SKILLS
Python, PyTorch, FastAPI, Docker, SQL, Machine Learning, NLP

CERTIFICATIONS
AWS Certified Cloud Practitioner — Amazon Web Services"""

    jd_text = """Senior AI/ML Engineer
We are seeking a Senior AI/ML Engineer to build scalable microservices, REST APIs, Docker containers, PyTorch models, and Cloud architecture.
Key skills: Python, PyTorch, FastAPI, Docker, Microservices, Cloud, REST APIs."""

    # 1. Test parsing complete resume & formatting text
    from app.utils.file_utils import format_resume_to_text
    parsed = temp_service.import_resume(base_text)
    assert parsed.personal_info.full_name == "Nandini Ande"
    assert parsed.personal_info.email == "andenandini183@gmail.com"
    assert len(parsed.experience) > 0
    assert parsed.experience[0].position == "AI Developer Intern"
    assert len(parsed.education) > 0
    assert len(parsed.projects) > 0
    assert len(parsed.skills) > 0
    assert len(parsed.certifications) > 0

    formatted_str = format_resume_to_text(parsed)
    assert "Nandini Ande" in formatted_str
    assert "WORK EXPERIENCE & INTERNSHIPS" in formatted_str

    # 2. Test building tailored resume from JD
    tailored_resume, jd_result = temp_service.build_new_resume_from_jd(base_text, jd_text)
    assert tailored_resume.id is not None
    assert "Senior AI/ML Engineer" in tailored_resume.personal_info.title or "Tailored" in tailored_resume.title
    assert len(tailored_resume.experience) == len(parsed.experience)
    assert len(tailored_resume.education) == len(parsed.education)
    assert len(tailored_resume.projects) == len(parsed.projects)
    assert len(tailored_resume.skills) >= len(parsed.skills)
    assert len(tailored_resume.certifications) == len(parsed.certifications)
    assert jd_result.score >= 70

