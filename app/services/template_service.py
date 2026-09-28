"""
Template Service.
Manages available template registry and template switching.
"""

from typing import Dict, List, Optional
from app.templates.base_template import BaseTemplate
from app.templates.modern import ModernTemplate
from app.templates.professional import ProfessionalTemplate
from app.templates.minimal import MinimalTemplate
from app.templates.creative import CreativeTemplate
from app.config.settings import DEFAULT_TEMPLATE


class TemplateService:
    """Manages application resume templates."""

    def __init__(self):
        self._templates: Dict[str, BaseTemplate] = {
            "modern": ModernTemplate(),
            "professional": ProfessionalTemplate(),
            "minimal": MinimalTemplate(),
            "creative": CreativeTemplate(),
        }

    def get_template(self, name: str) -> BaseTemplate:
        """Retrieves template instance by key, falling back to default template."""
        key = (name or "").lower().strip()
        return self._templates.get(key, self._templates[DEFAULT_TEMPLATE])

    def get_all_templates(self) -> List[BaseTemplate]:
        """Returns list of all available template instances."""
        return list(self._templates.values())

    def get_template_names(self) -> List[str]:
        """Returns list of template keys."""
        return list(self._templates.keys())
