"""
Unit Tests for ATS Analyzer and Job Description Matcher.
"""

import pytest
from app.models import Resume, Education, Experience, Skill
from app.services.ats_analyzer import ATSAnalyzer


def test_ats_analyzer_empty_resume():
    analyzer = ATSAnalyzer()
    r = Resume()
    result = analyzer.analyze(r)

    assert result.score < 50
    assert len(result.critical_issues) > 0
    assert "Missing Full Name" in result.critical_issues[0] or "Missing or invalid Email" in result.critical_issues[0]


def test_ats_analyzer_complete_resume():
    analyzer = ATSAnalyzer()
    r = Resume()
    r.personal_info.full_name = "Jane Architect"
    r.personal_info.email = "jane@example.com"
    r.personal_info.phone = "+1-555-0199"
    r.personal_info.location = "San Francisco, CA"
    r.personal_info.linkedin = "https://linkedin.com/in/janeararchitect"
    r.personal_info.summary = "Experienced Cloud Architect with 10+ years driving scalable Python and AWS infrastructure."

    r.education.append(Education(institution="UC Berkeley", degree="BS", field_of_study="Computer Science"))
    r.experience.append(Experience(
        company="TechCorp",
        position="Principal Architect",
        responsibilities="Led cross-functional team. Architected Python and Docker microservices on AWS cloud."
    ))
    r.skills.append(Skill(skill_name="Python"))
    r.skills.append(Skill(skill_name="Docker"))
    r.skills.append(Skill(skill_name="AWS"))
    r.skills.append(Skill(skill_name="SQL"))

    result = analyzer.analyze(r)
    assert result.score >= 70
    assert "python" in result.detected_keywords
    assert "docker" in result.detected_keywords
    assert "aws" in result.detected_keywords


def test_jd_matching_and_tailoring():
    analyzer = ATSAnalyzer()
    r = Resume()
    r.personal_info.full_name = "Alex Developer"
    r.skills.append(Skill(skill_name="Python"))

    jd_text = """Senior Python Developer
    We are seeking a Senior Python Developer experienced with Django, React, PostgreSQL, Docker, and Kubernetes.
    Must have strong REST API skills."""

    jd_result = analyzer.analyze_job_description(r, jd_text)
    assert jd_result.score > 0
    assert "python" in jd_result.matched_keywords
    assert "docker" in jd_result.missing_keywords or "django" in jd_result.missing_keywords

    tailored_resume, updated_result = analyzer.tailor_resume_for_jd(r, jd_text)
    assert len(tailored_resume.skills) > 1
    assert any(s.category == "Job Tailored Skills" for s in tailored_resume.skills)
    assert updated_result.score >= jd_result.score
