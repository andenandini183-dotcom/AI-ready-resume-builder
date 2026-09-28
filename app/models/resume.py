"""
Resume Aggregate Root Model.
Encapsulates metadata and structured child section collections.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.personal_info import PersonalInfo
from app.models.education import Education
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.models.certification import Certification
from app.config.settings import DEFAULT_TEMPLATE


@dataclass
class Resume:
    id: Optional[int] = None
    title: str = "Untitled Resume"
    template_name: str = DEFAULT_TEMPLATE
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    education: List[Education] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converts complete resume object graph to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "template_name": self.template_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "personal_info": self.personal_info.to_dict(),
            "education": [e.to_dict() for e in self.education],
            "experience": [exp.to_dict() for exp in self.experience],
            "projects": [p.to_dict() for p in self.projects],
            "skills": [s.to_dict() for s in self.skills],
            "certifications": [c.to_dict() for c in self.certifications],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resume":
        """Reconstructs Resume aggregate from nested dictionary representation."""
        if not data:
            return cls()
            
        personal_data = data.get("personal_info", {})
        personal_info = PersonalInfo.from_dict(personal_data) if isinstance(personal_data, dict) else PersonalInfo()
        
        education_list = [Education.from_dict(e) for e in data.get("education", [])]
        experience_list = [Experience.from_dict(exp) for exp in data.get("experience", [])]
        projects_list = [Project.from_dict(p) for p in data.get("projects", [])]
        skills_list = [Skill.from_dict(s) for s in data.get("skills", [])]
        certs_list = [Certification.from_dict(c) for c in data.get("certifications", [])]
        
        return cls(
            id=data.get("id"),
            title=data.get("title", "Untitled Resume"),
            template_name=data.get("template_name", DEFAULT_TEMPLATE),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            updated_at=data.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            personal_info=personal_info,
            education=education_list,
            experience=experience_list,
            projects=projects_list,
            skills=skills_list,
            certifications=certs_list,
        )
