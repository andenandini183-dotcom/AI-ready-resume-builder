"""
Database Schema Definition and Initializer.
Defines table creation DDL, foreign keys, and indexes.
"""

import sqlite3
from app.utils.logger import logger

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        template_name TEXT NOT NULL DEFAULT 'modern',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS personal_info (
        resume_id INTEGER PRIMARY KEY,
        full_name TEXT DEFAULT '',
        title TEXT DEFAULT '',
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        location TEXT DEFAULT '',
        linkedin TEXT DEFAULT '',
        github TEXT DEFAULT '',
        portfolio TEXT DEFAULT '',
        summary TEXT DEFAULT '',
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        institution TEXT DEFAULT '',
        degree TEXT DEFAULT '',
        field_of_study TEXT DEFAULT '',
        start_date TEXT DEFAULT '',
        end_date TEXT DEFAULT '',
        gpa TEXT DEFAULT '',
        description TEXT DEFAULT '',
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        company TEXT DEFAULT '',
        position TEXT DEFAULT '',
        location TEXT DEFAULT '',
        start_date TEXT DEFAULT '',
        end_date TEXT DEFAULT '',
        is_current INTEGER DEFAULT 0,
        responsibilities TEXT DEFAULT '',
        achievements TEXT DEFAULT '',
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        project_name TEXT DEFAULT '',
        description TEXT DEFAULT '',
        technologies TEXT DEFAULT '',
        start_date TEXT DEFAULT '',
        end_date TEXT DEFAULT '',
        project_url TEXT DEFAULT '',
        github_url TEXT DEFAULT '',
        key_contributions TEXT DEFAULT '',
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        skill_name TEXT DEFAULT '',
        category TEXT DEFAULT 'Technical Skills',
        proficiency TEXT DEFAULT '',
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS certifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        name TEXT DEFAULT '',
        issuing_organization TEXT DEFAULT '',
        issue_date TEXT DEFAULT '',
        expiration_date TEXT DEFAULT '',
        credential_id TEXT DEFAULT '',
        credential_url TEXT DEFAULT '',
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );
    """,
    # Indexes for quick child lookups
    "CREATE INDEX IF NOT EXISTS idx_education_resume_id ON education(resume_id);",
    "CREATE INDEX IF NOT EXISTS idx_experience_resume_id ON experience(resume_id);",
    "CREATE INDEX IF NOT EXISTS idx_projects_resume_id ON projects(resume_id);",
    "CREATE INDEX IF NOT EXISTS idx_skills_resume_id ON skills(resume_id);",
    "CREATE INDEX IF NOT EXISTS idx_certifications_resume_id ON certifications(resume_id);",
]


def create_tables(conn: sqlite3.Connection) -> None:
    """Executes schema DDL statements to create database structure."""
    cursor = conn.cursor()
    for statement in DDL_STATEMENTS:
        cursor.execute(statement)
    conn.commit()
    logger.info("Database schema initialized successfully.")
