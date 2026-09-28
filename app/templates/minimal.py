"""
Minimal Resume Template.
High contrast, typography-first layout with clean lines and spacious margins.
"""

from app.templates.base_template import BaseTemplate


class MinimalTemplate(BaseTemplate):
    """Minimalist typography resume template layout implementation."""

    @property
    def name(self) -> str:
        return "minimal"

    @property
    def display_name(self) -> str:
        return "Minimal"

    @property
    def description(self) -> str:
        return "Sleek, typography-focused layout with subtle gray borders."

    @property
    def primary_color(self) -> str:
        return "#18181B"  # Dark Charcoal

    @property
    def secondary_color(self) -> str:
        return "#52525B"  # Neutral Gray

    @property
    def accent_color(self) -> str:
        return "#3F3F46"  # Zinc Accent

    @property
    def layout_style(self) -> str:
        return "minimal_clean"
