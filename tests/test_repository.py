"""
Integration Tests for SQLite Resume Repository.
"""

import pytest
from app.database.connection import DatabaseConnection
from app.database.repository import ResumeRepository
from app.models import Resume, Education, Experience, Skill


@pytest.fixture
def temp_repo(tmp_path):
    db_file = tmp_path / "test_resume.db"
    conn_mgr = DatabaseConnection(db_file)
    return ResumeRepository(conn_mgr)


def test_create_and_get_resume(temp_repo):
    resume = temp_repo.create_resume(title="Dev Resume", template_name="modern")
    assert resume.id is not None
    assert resume.title == "Dev Resume"

    fetched = temp_repo.get_resume(resume.id)
    assert fetched is not None
    assert fetched.title == "Dev Resume"


def test_update_resume_with_children(temp_repo):
    resume = temp_repo.create_resume(title="Original Title")
    resume.personal_info.full_name = "Bob Developer"
    resume.education.append(Education(institution="MIT", degree="MS"))
    resume.experience.append(Experience(company="Acme Corp", position="Engineer"))
    resume.skills.append(Skill(skill_name="Python"))

    updated = temp_repo.update_resume(resume)
    assert updated.personal_info.full_name == "Bob Developer"
    assert len(updated.education) == 1
    assert len(updated.experience) == 1
    assert len(updated.skills) == 1

    # Reload fresh from DB
    reloaded = temp_repo.get_resume(resume.id)
    assert reloaded.personal_info.full_name == "Bob Developer"
    assert reloaded.education[0].institution == "MIT"


def test_duplicate_resume(temp_repo):
    original = temp_repo.create_resume(title="Master Resume")
    original.personal_info.full_name = "Charlie"
    original.skills.append(Skill(skill_name="Docker"))
    temp_repo.update_resume(original)

    duplicate = temp_repo.duplicate_resume(original.id, new_title="Master Resume Copy")
    assert duplicate is not None
    assert duplicate.id != original.id
    assert duplicate.title == "Master Resume Copy"
    assert duplicate.personal_info.full_name == "Charlie"
    assert len(duplicate.skills) == 1


def test_delete_resume_cascade(temp_repo):
    resume = temp_repo.create_resume(title="To Be Deleted")
    resume.education.append(Education(institution="Harvard"))
    temp_repo.update_resume(resume)

    deleted = temp_repo.delete_resume(resume.id)
    assert deleted
    assert temp_repo.get_resume(resume.id) is None
