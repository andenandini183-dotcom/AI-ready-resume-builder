"""
Project Domain Model.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from app.utils.formatting import parse_bullet_list, clean_garbage_text


@dataclass
class Project:
    id: Optional[int] = None
    resume_id: Optional[int] = None
    project_name: str = ""
    description: str = ""
    technologies: str = ""
    start_date: str = ""
    end_date: str = ""
    project_url: str = ""
    github_url: str = ""
    key_contributions: str = ""

    def get_contributions_list(self) -> List[str]:
        """Returns key contributions strictly as extracted from the uploaded resume/user input without synthetic elaboration."""
        bullets = parse_bullet_list(self.key_contributions)
        
        if not bullets and self.description:
            bullets = parse_bullet_list(self.description)

        expanded_bullets: List[str] = []
        for b in bullets:
            clean_b = clean_garbage_text(b)
            if not clean_b:
                continue
            expanded_bullets.append(clean_b)

        seen = set()
        final_bullets: List[str] = []
        for b in expanded_bullets:
            if b.lower() not in seen:
                seen.add(b.lower())
                final_bullets.append(b)

        raw_tech = clean_garbage_text(self.technologies)
        has_tech_bullet = any("tech stack" in b.lower() or b.lower().startswith("tech:") for b in final_bullets)
        if not has_tech_bullet and raw_tech:
            final_bullets.append(f"Tech Stack: {raw_tech}")

        return final_bullets

    def to_dict(self) -> Dict[str, Any]:
        """Converts model instance to dictionary."""
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "project_name": clean_garbage_text(self.project_name),
            "description": clean_garbage_text(self.description),
            "technologies": clean_garbage_text(self.technologies),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "project_url": self.project_url,
            "github_url": self.github_url,
            "key_contributions": self.key_contributions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Constructs Project instance from dictionary."""
        return cls(
            id=data.get("id"),
            resume_id=data.get("resume_id"),
            project_name=clean_garbage_text(data.get("project_name", "")),
            description=clean_garbage_text(data.get("description", "")),
            technologies=clean_garbage_text(data.get("technologies", "")),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            project_url=data.get("project_url", ""),
            github_url=data.get("github_url", ""),
            key_contributions=data.get("key_contributions", ""),
        )

