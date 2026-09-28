"""
Resume Repository.
Encapsulates all SQLite CRUD operations, queries, transactions, duplication, and backup calls.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.database.connection import DatabaseConnection
from app.database.schema import create_tables
from app.models.resume import Resume
from app.models.personal_info import PersonalInfo
from app.models.education import Education
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.models.certification import Certification
from app.utils.file_utils import backup_database
from app.utils.logger import logger


class ResumeRepository:
    """Repository handling persistence for Resume entities."""

    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db_conn = db_connection or DatabaseConnection()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Initializes database schema on startup."""
        with self.db_conn.get_connection() as conn:
            create_tables(conn)

    def create_resume(self, title: str = "Untitled Resume", template_name: str = "modern") -> Resume:
        """Creates a new empty Resume record in database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resumes (title, template_name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (title, template_name, now, now)
            )
            resume_id = cursor.lastrowid
            
            # Initialize empty personal info
            cursor.execute(
                "INSERT INTO personal_info (resume_id) VALUES (?)",
                (resume_id,)
            )

        logger.info(f"Created new resume: ID {resume_id} ('{title}')")
        return self.get_resume(resume_id)  # type: ignore

    def get_resume(self, resume_id: int) -> Optional[Resume]:
        """Loads a complete Resume aggregate by ID with all child collections."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
            row = cursor.fetchone()
            if not row:
                return None
                
            resume = Resume(
                id=row["id"],
                title=row["title"],
                template_name=row["template_name"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

            # Load Personal Info
            cursor.execute("SELECT * FROM personal_info WHERE resume_id = ?", (resume_id,))
            p_row = cursor.fetchone()
            if p_row:
                resume.personal_info = PersonalInfo(
                    full_name=p_row["full_name"],
                    title=p_row["title"],
                    email=p_row["email"],
                    phone=p_row["phone"],
                    location=p_row["location"],
                    linkedin=p_row["linkedin"],
                    github=p_row["github"],
                    portfolio=p_row["portfolio"],
                    summary=p_row["summary"],
                )

            # Load Education
            cursor.execute("SELECT * FROM education WHERE resume_id = ? ORDER BY id ASC", (resume_id,))
            resume.education = [
                Education(
                    id=e["id"],
                    resume_id=e["resume_id"],
                    institution=e["institution"],
                    degree=e["degree"],
                    field_of_study=e["field_of_study"],
                    start_date=e["start_date"],
                    end_date=e["end_date"],
                    gpa=e["gpa"],
                    description=e["description"],
                )
                for e in cursor.fetchall()
            ]

            # Load Experience
            cursor.execute("SELECT * FROM experience WHERE resume_id = ? ORDER BY id ASC", (resume_id,))
            resume.experience = [
                Experience(
                    id=exp["id"],
                    resume_id=exp["resume_id"],
                    company=exp["company"],
                    position=exp["position"],
                    location=exp["location"],
                    start_date=exp["start_date"],
                    end_date=exp["end_date"],
                    is_current=bool(exp["is_current"]),
                    responsibilities=exp["responsibilities"],
                    achievements=exp["achievements"],
                )
                for exp in cursor.fetchall()
            ]

            # Load Projects
            cursor.execute("SELECT * FROM projects WHERE resume_id = ? ORDER BY id ASC", (resume_id,))
            resume.projects = [
                Project(
                    id=p["id"],
                    resume_id=p["resume_id"],
                    project_name=p["project_name"],
                    description=p["description"],
                    technologies=p["technologies"],
                    start_date=p["start_date"],
                    end_date=p["end_date"],
                    project_url=p["project_url"],
                    github_url=p["github_url"],
                    key_contributions=p["key_contributions"],
                )
                for p in cursor.fetchall()
            ]

            # Load Skills
            cursor.execute("SELECT * FROM skills WHERE resume_id = ? ORDER BY id ASC", (resume_id,))
            resume.skills = [
                Skill(
                    id=s["id"],
                    resume_id=s["resume_id"],
                    skill_name=s["skill_name"],
                    category=s["category"],
                    proficiency=s["proficiency"],
                )
                for s in cursor.fetchall()
            ]

            # Load Certifications
            cursor.execute("SELECT * FROM certifications WHERE resume_id = ? ORDER BY id ASC", (resume_id,))
            resume.certifications = [
                Certification(
                    id=c["id"],
                    resume_id=c["resume_id"],
                    name=c["name"],
                    issuing_organization=c["issuing_organization"],
                    issue_date=c["issue_date"],
                    expiration_date=c["expiration_date"],
                    credential_id=c["credential_id"],
                    credential_url=c["credential_url"],
                )
                for c in cursor.fetchall()
            ]

            return resume

    def get_all_resumes(self) -> List[Resume]:
        """Returns list of all resumes sorted by last updated timestamp."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM resumes ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [self.get_resume(row["id"]) for row in rows if self.get_resume(row["id"])]  # type: ignore

    def search_resumes(self, query: str) -> List[Resume]:
        """Filters resumes by title, name, or job title."""
        if not query or not query.strip():
            return self.get_all_resumes()
            
        q = f"%{query.strip()}%"
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT r.id FROM resumes r
                LEFT JOIN personal_info p ON r.id = p.resume_id
                WHERE r.title LIKE ? OR p.full_name LIKE ? OR p.title LIKE ?
                ORDER BY r.updated_at DESC
            """, (q, q, q))
            rows = cursor.fetchall()
            return [self.get_resume(row["id"]) for row in rows if self.get_resume(row["id"])]  # type: ignore

    def update_resume(self, resume: Resume) -> Resume:
        """Saves entire Resume aggregate to database in a single atomic transaction."""
        if not resume.id:
            raise ValueError("Cannot update resume without an ID.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resume.updated_at = now

        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update Resume metadata
            cursor.execute(
                "UPDATE resumes SET title = ?, template_name = ?, updated_at = ? WHERE id = ?",
                (resume.title, resume.template_name, now, resume.id)
            )

            # Update Personal Info (Upsert)
            p = resume.personal_info
            cursor.execute("""
                INSERT INTO personal_info (resume_id, full_name, title, email, phone, location, linkedin, github, portfolio, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resume_id) DO UPDATE SET
                    full_name=excluded.full_name,
                    title=excluded.title,
                    email=excluded.email,
                    phone=excluded.phone,
                    location=excluded.location,
                    linkedin=excluded.linkedin,
                    github=excluded.github,
                    portfolio=excluded.portfolio,
                    summary=excluded.summary
            """, (resume.id, p.full_name, p.title, p.email, p.phone, p.location, p.linkedin, p.github, p.portfolio, p.summary))

            # Sync Child collections (Replace with updated state)
            cursor.execute("DELETE FROM education WHERE resume_id = ?", (resume.id,))
            for edu in resume.education:
                cursor.execute("""
                    INSERT INTO education (resume_id, institution, degree, field_of_study, start_date, end_date, gpa, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (resume.id, edu.institution, edu.degree, edu.field_of_study, edu.start_date, edu.end_date, edu.gpa, edu.description))

            cursor.execute("DELETE FROM experience WHERE resume_id = ?", (resume.id,))
            for exp in resume.experience:
                cursor.execute("""
                    INSERT INTO experience (resume_id, company, position, location, start_date, end_date, is_current, responsibilities, achievements)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (resume.id, exp.company, exp.position, exp.location, exp.start_date, exp.end_date, 1 if exp.is_current else 0, exp.responsibilities, exp.achievements))

            cursor.execute("DELETE FROM projects WHERE resume_id = ?", (resume.id,))
            for proj in resume.projects:
                cursor.execute("""
                    INSERT INTO projects (resume_id, project_name, description, technologies, start_date, end_date, project_url, github_url, key_contributions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (resume.id, proj.project_name, proj.description, proj.technologies, proj.start_date, proj.end_date, proj.project_url, proj.github_url, proj.key_contributions))

            cursor.execute("DELETE FROM skills WHERE resume_id = ?", (resume.id,))
            for sk in resume.skills:
                cursor.execute("""
                    INSERT INTO skills (resume_id, skill_name, category, proficiency)
                    VALUES (?, ?, ?, ?)
                """, (resume.id, sk.skill_name, sk.category, sk.proficiency))

            cursor.execute("DELETE FROM certifications WHERE resume_id = ?", (resume.id,))
            for cert in resume.certifications:
                cursor.execute("""
                    INSERT INTO certifications (resume_id, name, issuing_organization, issue_date, expiration_date, credential_id, credential_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (resume.id, cert.name, cert.issuing_organization, cert.issue_date, cert.expiration_date, cert.credential_id, cert.credential_url))

        logger.info(f"Updated resume ID {resume.id} successfully.")
        return self.get_resume(resume.id)  # type: ignore

    def delete_resume(self, resume_id: int) -> bool:
        """Deletes a resume and cascaded child records safely."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted resume ID {resume_id}")
            return deleted

    def duplicate_resume(self, resume_id: int, new_title: Optional[str] = None) -> Optional[Resume]:
        """Deep-copies an existing resume along with all child entries."""
        original = self.get_resume(resume_id)
        if not original:
            return None

        title = new_title or f"{original.title} (Copy)"
        new_resume = self.create_resume(title=title, template_name=original.template_name)

        # Copy data
        new_resume.personal_info = PersonalInfo.from_dict(original.personal_info.to_dict())
        new_resume.education = [Education.from_dict(e.to_dict()) for e in original.education]
        new_resume.experience = [Experience.from_dict(exp.to_dict()) for exp in original.experience]
        new_resume.projects = [Project.from_dict(p.to_dict()) for p in original.projects]
        new_resume.skills = [Skill.from_dict(s.to_dict()) for s in original.skills]
        new_resume.certifications = [Certification.from_dict(c.to_dict()) for c in original.certifications]

        return self.update_resume(new_resume)

    def backup(self) -> Path:
        """Triggers local snapshot backup of database."""
        return backup_database()
