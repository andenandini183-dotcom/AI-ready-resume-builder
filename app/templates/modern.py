"""
Modern Resume Template.
Features a clean modern layout with a bold navy header and blue accent accents.
"""

from app.templates.base_template import BaseTemplate


class ModernTemplate(BaseTemplate):
    """Modern resume template layout implementation."""

    @property
    def name(self) -> str:
        return "modern"

    @property
    def display_name(self) -> str:
        return "Modern"

    @property
    def description(self) -> str:
        return "Clean modern layout with bold headers and blue accent styling."

    @property
    def primary_color(self) -> str:
        return "#1E293B"  # Slate Navy

    @property
    def secondary_color(self) -> str:
        return "#475569"  # Slate Gray

    @property
    def accent_color(self) -> str:
        return "#2563EB"  # Royal Blue

    @property
    def layout_style(self) -> str:
        return "modern_clean"
