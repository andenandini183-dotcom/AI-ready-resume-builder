"""
Experience Domain Model.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from app.utils.formatting import parse_bullet_list


@dataclass
class Experience:
    id: Optional[int] = None
    resume_id: Optional[int] = None
    company: str = ""
    position: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    is_current: bool = False
    responsibilities: str = ""
    achievements: str = ""

    def get_responsibilities_list(self) -> List[str]:
        """Returns responsibilities formatted as list of bullet strings."""
        return parse_bullet_list(self.responsibilities)

    def get_achievements_list(self) -> List[str]:
        """Returns achievements formatted as list of bullet strings."""
        return parse_bullet_list(self.achievements)

    def to_dict(self) -> Dict[str, Any]:
        """Converts model instance to dictionary."""
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "company": self.company,
            "position": self.position,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_current": self.is_current,
            "responsibilities": self.responsibilities,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experience":
        """Constructs Experience instance from dictionary."""
        return cls(
            id=data.get("id"),
            resume_id=data.get("resume_id"),
            company=data.get("company", ""),
            position=data.get("position", ""),
            location=data.get("location", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            is_current=bool(data.get("is_current", False)),
            responsibilities=data.get("responsibilities", ""),
            achievements=data.get("achievements", ""),
        )
