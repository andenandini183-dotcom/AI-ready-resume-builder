"""
Resume Application Service Coordinator.
Central entry point for all business logic, persistence orchestration, exports, ATS analysis, and JD tailoring.
Includes clean extension hooks for future AI modules.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple, Union

from app.models.resume import Resume
from app.database.repository import ResumeRepository
from app.services.template_service import TemplateService
from app.services.ats_analyzer import ATSAnalyzer, ATSResult, JDATSResult
from app.services.export_service import ExportService
from app.utils.file_utils import parse_resume_import
from app.utils.logger import logger


class ResumeService:
    """Core application business logic coordinator."""

    def __init__(
        self,
        repository: Optional[ResumeRepository] = None,
        template_service: Optional[TemplateService] = None,
        ats_analyzer: Optional[ATSAnalyzer] = None,
        export_service: Optional[ExportService] = None,
    ):
        self.repository = repository or ResumeRepository()
        self.template_service = template_service or TemplateService()
        self.ats_analyzer = ats_analyzer or ATSAnalyzer()
        self.export_service = export_service or ExportService()

    # --- CRUD & Persistence ---

    def create_resume(self, title: str = "Untitled Resume", template_name: str = "modern") -> Resume:
        """Creates a new resume record."""
        return self.repository.create_resume(title=title, template_name=template_name)

    def get_resume(self, resume_id: int) -> Optional[Resume]:
        """Loads a resume by ID."""
        return self.repository.get_resume(resume_id)

    def get_all_resumes(self) -> List[Resume]:
        """Loads all saved resumes."""
        return self.repository.get_all_resumes()

    def search_resumes(self, query: str) -> List[Resume]:
        """Filters resumes by search keyword."""
        return self.repository.search_resumes(query)

    def update_resume(self, resume: Resume) -> Resume:
        """Saves changes to a resume."""
        return self.repository.update_resume(resume)

    def delete_resume(self, resume_id: int) -> bool:
        """Deletes a resume."""
        return self.repository.delete_resume(resume_id)

    def duplicate_resume(self, resume_id: int, new_title: Optional[str] = None) -> Optional[Resume]:
        """Deep-copies an existing resume."""
        return self.repository.duplicate_resume(resume_id, new_title)

    def backup_database(self) -> Path:
        """Triggers local database backup snapshot."""
        return self.repository.backup()

    def import_resume(self, file_path_or_content: Union[Path, str]) -> Resume:
        """Imports resume from JSON file, text file, or raw text and saves it to DB."""
        parsed = parse_resume_import(file_path_or_content)
        created = self.create_resume(title=parsed.title or "Imported Resume", template_name=parsed.template_name)
        parsed.id = created.id
        return self.update_resume(parsed)

    # --- ATS Analysis, JD Matcher & PDF Export ---

    def analyze_ats(self, resume: Resume) -> ATSResult:
        """Runs offline deterministic ATS analysis on resume."""
        return self.ats_analyzer.analyze(resume)

    def analyze_jd_match(self, resume: Resume, job_description: str) -> JDATSResult:
        """Analyzes how well the resume matches a target Job Description."""
        return self.ats_analyzer.analyze_job_description(resume, job_description)

    def tailor_resume_for_jd(self, resume: Resume, job_description: str) -> Tuple[Resume, JDATSResult]:
        """Auto-tailors resume skills/title to align with Job Description and saves changes."""
        tailored_resume, jd_result = self.ats_analyzer.tailor_resume_for_jd(resume, job_description)
        if tailored_resume.id:
            tailored_resume = self.update_resume(tailored_resume)
        return tailored_resume, jd_result

    def build_new_resume_from_jd(
        self,
        base_input: Union[Resume, Path, str],
        job_description: str,
    ) -> Tuple[Resume, JDATSResult]:
        """Builds and persists a BRAND NEW tailored resume generated specifically for a target Job Description."""
        if isinstance(base_input, Resume):
            base_resume = base_input
        else:
            base_resume = parse_resume_import(base_input)

        tailored_data, jd_result = self.ats_analyzer.build_tailored_resume_from_jd(base_resume, job_description)
        
        # Save as new resume record in DB
        created = self.create_resume(title=tailored_data.title, template_name=tailored_data.template_name)
        tailored_data.id = created.id
        saved_resume = self.update_resume(tailored_data)
        
        return saved_resume, jd_result

    def export_pdf(self, resume: Resume, target_path: Optional[Path] = None, open_after: bool = False) -> Path:
        """Generates PDF resume file."""
        pdf_path = self.export_service.export_pdf(resume, target_path)
        if open_after:
            self.export_service.open_pdf_in_system_viewer(pdf_path)
        return pdf_path

    # --- Extension Hooks for Future AI Integration (Section 20 Architecture) ---

    def ai_improve_bullet(self, bullet_text: str) -> str:
        """Extension point for future LLM bullet improvement."""
        cleaned = bullet_text.strip()
        if not cleaned:
            return ""
        logger.info("AI extension point triggered: ai_improve_bullet")
        return cleaned

    def ai_generate_summary(self, resume: Resume) -> str:
        """Extension point for future LLM professional summary generation."""
        logger.info("AI extension point triggered: ai_generate_summary")
        name = resume.personal_info.full_name or "Professional"
        title = resume.personal_info.title or "Specialist"
        return f"Results-driven {title} with proven expertise in delivering high-impact projects and scalable solutions."

    def ai_match_job_description(self, resume: Resume, job_description: str) -> Dict[str, Any]:
        """Extension point for future LLM Job Description matching & gap analysis."""
        logger.info("AI extension point triggered: ai_match_job_description")
        jd_res = self.analyze_jd_match(resume, job_description)
        return jd_res.to_dict()
