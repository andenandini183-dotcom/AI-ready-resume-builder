"""
Unit Tests for Domain Models and Validators.
"""

import pytest
from app.models import Resume, PersonalInfo, Education, Experience, Project, Skill, Certification
from app.utils.validators import validate_email, validate_phone, validate_url, validate_required


def test_personal_info_model():
    p = PersonalInfo(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="+1-555-0199",
        summary="Experienced engineer.",
    )
    data = p.to_dict()
    assert data["full_name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    
    p2 = PersonalInfo.from_dict(data)
    assert p2.full_name == p.full_name
    assert p2.phone == p.phone


def test_resume_aggregate_model():
    r = Resume(title="Software Engineer Resume", template_name="modern")
    r.personal_info.full_name = "Alice Smith"
    r.education.append(Education(institution="Stanford", degree="BS", field_of_study="CS"))
    r.experience.append(Experience(company="Google", position="Senior Engineer", responsibilities="Led team."))
    r.skills.append(Skill(skill_name="Python", category="Programming"))

    data = r.to_dict()
    assert data["title"] == "Software Engineer Resume"
    assert len(data["education"]) == 1
    assert len(data["experience"]) == 1

    r2 = Resume.from_dict(data)
    assert r2.title == r.title
    assert r2.personal_info.full_name == "Alice Smith"
    assert r2.education[0].institution == "Stanford"
    assert r2.experience[0].company == "Google"
    assert r2.skills[0].skill_name == "Python"


def test_validators():
    valid, err = validate_email("user@example.com")
    assert valid
    assert err is None

    valid, err = validate_email("invalid-email")
    assert not valid
    assert "valid email" in err.lower()

    valid, err = validate_phone("+1-555-0199")
    assert valid

    valid, err = validate_url("https://linkedin.com/in/john")
    assert valid

    valid, err = validate_required("Text", "Title")
    assert valid

    valid, err = validate_required("", "Title")
    assert not valid


def test_btech_education_parsing_and_formatting():
    from app.utils.file_utils import parse_resume_import
    from app.templates.modern import ModernTemplate

    text = """Nandini Ande
andenandini183@gmail.com

EDUCATION
B.Tech in Artificial Intelligence & Machine Learning — ABC Institute of Technology
2022 - 2026"""

    r = parse_resume_import(text)
    assert len(r.education) == 1
    edu = r.education[0]
    assert "Bachelor of Technology" in edu.degree or "B.Tech" in edu.degree
    assert "Artificial Intelligence" in edu.field_of_study or "Artificial Intelligence" in edu.degree
    assert edu.institution == "ABC Institute of Technology"

    # Test rendering structure
    tmpl = ModernTemplate()
    rendered = tmpl.render_structure(r)
    edu_rendered = rendered["education"][0]
    assert "Bachelor of Technology" in edu_rendered["degree"] or "B.Tech" in edu_rendered["degree"]
    assert "Artificial Intelligence" in edu_rendered["degree"]
    assert not edu_rendered["degree"].endswith(" in")

