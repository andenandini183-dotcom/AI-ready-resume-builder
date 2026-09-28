"""
Base Resume Template Interface.
Provides abstract contract and common rendering structure for all resume templates.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.models.resume import Resume
from app.utils.formatting import format_contact_info, format_date_range


class BaseTemplate(ABC):
    """Abstract Base Class for Resume Templates."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique key name of the template."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """User-friendly display name of the template."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short visual description of the template layout."""
        pass

    @property
    def primary_color(self) -> str:
        return "#1E293B"  # Default Dark Slate

    @property
    def secondary_color(self) -> str:
        return "#475569"  # Slate Muted

    @property
    def accent_color(self) -> str:
        return "#2563EB"  # Royal Blue

    @property
    def font_family(self) -> str:
        return "Helvetica"

    @property
    def layout_style(self) -> str:
        return "single_column"  # single_column, two_column, sidebar

    def render_structure(self, resume: Resume) -> Dict[str, Any]:
        """Processes structured Resume model into layout components for PDF and Preview engines."""
        info = resume.personal_info
        
        header = {
            "name": info.full_name or "Your Full Name",
            "title": info.title or "Professional Title",
            "contact_line": format_contact_info(info.location, info.email, info.phone, info.linkedin, info.github),
            "email": info.email,
            "phone": info.phone,
            "location": info.location,
            "linkedin": info.linkedin,
            "github": info.github,
            "portfolio": info.portfolio,
            "summary": info.summary,
        }

        experience_blocks = [
            {
                "company": exp.company,
                "position": exp.position,
                "location": exp.location,
                "date_range": format_date_range(exp.start_date, exp.end_date, exp.is_current),
                "responsibilities": exp.get_responsibilities_list(),
                "achievements": exp.get_achievements_list(),
            }
            for exp in resume.experience
        ]

        education_blocks = []
        for edu in resume.education:
            deg = edu.degree.strip() if edu.degree else ""
            field = edu.field_of_study.strip() if edu.field_of_study else ""
            
            if deg and field and field.lower() not in deg.lower():
                full_deg = f"{deg} in {field}"
            elif deg:
                full_deg = deg
            elif field:
                full_deg = field
            else:
                full_deg = "Education Qualification"

            education_blocks.append({
                "institution": edu.institution or "Institution",
                "degree": full_deg,
                "date_range": format_date_range(edu.start_date, edu.end_date),
                "gpa": f"GPA: {edu.gpa}" if edu.gpa else "",
                "description": edu.description,
            })

        project_blocks = [
            {
                "name": proj.project_name,
                "technologies": proj.technologies,
                "date_range": format_date_range(proj.start_date, proj.end_date),
                "description": proj.description,
                "url": proj.project_url or proj.github_url,
                "contributions": proj.get_contributions_list(),
            }
            for proj in resume.projects
        ]

        # Group skills by category
        skills_by_category: Dict[str, List[str]] = {}
        for sk in resume.skills:
            cat = sk.category or "Technical Skills"
            label = f"{sk.skill_name} ({sk.proficiency})" if sk.proficiency else sk.skill_name
            if cat not in skills_by_category:
                skills_by_category[cat] = []
            skills_by_category[cat].append(label)

        cert_blocks = [
            {
                "name": cert.name,
                "organization": cert.issuing_organization,
                "date": cert.issue_date,
                "credential_id": cert.credential_id,
                "url": cert.credential_url,
            }
            for cert in resume.certifications
        ]

        return {
            "template_name": self.name,
            "layout_style": self.layout_style,
            "colors": {
                "primary": self.primary_color,
                "secondary": self.secondary_color,
                "accent": self.accent_color,
            },
            "font_family": self.font_family,
            "header": header,
            "summary": info.summary,
            "experience": experience_blocks,
            "education": education_blocks,
            "projects": project_blocks,
            "skills": skills_by_category,
            "certifications": cert_blocks,
        }
