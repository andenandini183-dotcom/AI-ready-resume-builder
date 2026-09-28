"""
Education Entry Domain Model.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Education:
    id: Optional[int] = None
    resume_id: Optional[int] = None
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts model instance to dictionary."""
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "institution": self.institution,
            "degree": self.degree,
            "field_of_study": self.field_of_study,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gpa": self.gpa,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Education":
        """Constructs Education instance from dictionary."""
        return cls(
            id=data.get("id"),
            resume_id=data.get("resume_id"),
            institution=data.get("institution", ""),
            degree=data.get("degree", ""),
            field_of_study=data.get("field_of_study", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            gpa=data.get("gpa", ""),
            description=data.get("description", ""),
        )
