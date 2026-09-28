"""
Integration Tests for PDF Generator across all templates.
"""

import pytest
from pathlib import Path
from app.models import Resume, Education, Experience, Project, Skill, Certification
from app.services.pdf_generator import PDFGenerator


@pytest.fixture
def sample_resume():
    r = Resume(title="PDF Test Resume")
    r.personal_info.full_name = "Eleanor Vance"
    r.personal_info.title = "Lead Solutions Architect"
    r.personal_info.email = "eleanor@example.com"
    r.personal_info.phone = "+1-555-0188"
    r.personal_info.location = "New York, NY"
    r.personal_info.linkedin = "https://linkedin.com/in/eleanor"
    r.personal_info.github = "https://github.com/eleanor"
    r.personal_info.summary = "Passionate lead architect with expertise in cloud native solutions, microservices, and team leadership."

    r.education.append(Education(institution="Columbia University", degree="MS", field_of_study="Computer Engineering", start_date="2016", end_date="2018", gpa="3.9"))
    r.experience.append(Experience(
        company="FinTech Inc",
        position="Senior Architect",
        location="New York, NY",
        start_date="2018-06",
        end_date="Present",
        is_current=True,
        responsibilities="Led engineering team of 12. Designed scalable Python API Gateway handling 5M daily requests.",
        achievements="Reduced infrastructure costs by 35% through Docker container optimization."
    ))
    r.projects.append(Project(
        project_name="Cloud Platform Gateway",
        description="High-throughput API gateway service.",
        technologies="Python, FastAPI, Redis, Docker",
        key_contributions="Architected async request router."
    ))
    r.skills.append(Skill(skill_name="Python", category="Programming"))
    r.skills.append(Skill(skill_name="Docker", category="DevOps"))
    r.skills.append(Skill(skill_name="PostgreSQL", category="Databases"))
    r.certifications.append(Certification(name="AWS Solutions Architect", issuing_organization="Amazon Web Services", issue_date="2021"))
    return r


@pytest.mark.parametrize("template_name", ["modern", "professional", "minimal", "creative"])
def test_pdf_generation_all_templates(tmp_path, sample_resume, template_name):
    pdf_gen = PDFGenerator()
    sample_resume.template_name = template_name
    output_pdf = tmp_path / f"test_{template_name}.pdf"

    result_path = pdf_gen.generate(sample_resume, output_pdf)

    assert result_path.exists()
    assert result_path.stat().st_size > 0

    # Verify standard PDF header bytes magic number %PDF
    with open(result_path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"
