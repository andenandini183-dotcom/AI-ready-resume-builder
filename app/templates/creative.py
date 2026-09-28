"""
Creative Resume Template.
Stylish left sidebar visual template highlighting skills and contact details alongside experience.
"""

from app.templates.base_template import BaseTemplate


class CreativeTemplate(BaseTemplate):
    """Creative resume template layout implementation."""

    @property
    def name(self) -> str:
        return "creative"

    @property
    def display_name(self) -> str:
        return "Creative"

    @property
    def description(self) -> str:
        return "Vibrant template with colored header, accent badges, and dynamic layout."

    @property
    def primary_color(self) -> str:
        return "#4C1D95"  # Deep Purple

    @property
    def secondary_color(self) -> str:
        return "#6D28D9"  # Royal Purple

    @property
    def accent_color(self) -> str:
        return "#7C3AED"  # Bright Violet

    @property
    def layout_style(self) -> str:
        return "creative_sidebar"
