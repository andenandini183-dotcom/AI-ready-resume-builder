"""
Professional Resume Template.
Traditional corporate layout with prominent top hierarchy and dark blue accents.
"""

from app.templates.base_template import BaseTemplate


class ProfessionalTemplate(BaseTemplate):
    """Professional corporate resume template layout implementation."""

    @property
    def name(self) -> str:
        return "professional"

    @property
    def display_name(self) -> str:
        return "Professional"

    @property
    def description(self) -> str:
        return "Classic executive corporate template with structured section dividers."

    @property
    def primary_color(self) -> str:
        return "#0F172A"  # Dark Executive Navy

    @property
    def secondary_color(self) -> str:
        return "#334155"  # Slate Muted

    @property
    def accent_color(self) -> str:
        return "#0284C7"  # Deep Sky Blue

    @property
    def layout_style(self) -> str:
        return "single_column"
