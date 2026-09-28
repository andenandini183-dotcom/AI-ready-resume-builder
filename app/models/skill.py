"""
Skill Domain Model.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Skill:
    id: Optional[int] = None
    resume_id: Optional[int] = None
    skill_name: str = ""
    category: str = "Technical Skills"
    proficiency: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts model instance to dictionary."""
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "skill_name": self.skill_name,
            "category": self.category,
            "proficiency": self.proficiency,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """Constructs Skill instance from dictionary."""
        return cls(
            id=data.get("id"),
            resume_id=data.get("resume_id"),
            skill_name=data.get("skill_name", ""),
            category=data.get("category", "Technical Skills"),
            proficiency=data.get("proficiency", ""),
        )
