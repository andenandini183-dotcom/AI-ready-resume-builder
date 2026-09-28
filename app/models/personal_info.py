"""
Personal Information Domain Model.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class PersonalInfo:
    full_name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts model instance to dictionary."""
        return {
            "full_name": self.full_name,
            "title": self.title,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "github": self.github,
            "portfolio": self.portfolio,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonalInfo":
        """Constructs PersonalInfo instance from dictionary."""
        if not data:
            return cls()
        return cls(
            full_name=data.get("full_name", ""),
            title=data.get("title", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            location=data.get("location", ""),
            linkedin=data.get("linkedin", ""),
            github=data.get("github", ""),
            portfolio=data.get("portfolio", ""),
            summary=data.get("summary", ""),
        )
