"""
Certification Domain Model.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Certification:
    id: Optional[int] = None
    resume_id: Optional[int] = None
    name: str = ""
    issuing_organization: str = ""
    issue_date: str = ""
    expiration_date: str = ""
    credential_id: str = ""
    credential_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converts model instance to dictionary."""
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "name": self.name,
            "issuing_organization": self.issuing_organization,
            "issue_date": self.issue_date,
            "expiration_date": self.expiration_date,
            "credential_id": self.credential_id,
            "credential_url": self.credential_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Certification":
        """Constructs Certification instance from dictionary."""
        return cls(
            id=data.get("id"),
            resume_id=data.get("resume_id"),
            name=data.get("name", ""),
            issuing_organization=data.get("issuing_organization", ""),
            issue_date=data.get("issue_date", ""),
            expiration_date=data.get("expiration_date", ""),
            credential_id=data.get("credential_id", ""),
            credential_url=data.get("credential_url", ""),
        )
