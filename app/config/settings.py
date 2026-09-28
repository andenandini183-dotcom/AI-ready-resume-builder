"""
Application Configuration and Settings.
Centralizes paths, UI themes, database locations, default settings, and directory initializations.
"""

from pathlib import Path
import sys

# Base Application Directory (root of the repository)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data & Output Directories
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
OUTPUT_DIR = BASE_DIR / "output" / "generated_resumes"
ASSETS_DIR = BASE_DIR / "assets"

# File Paths
DATABASE_PATH = DATA_DIR / "resume_builder.db"
LOG_FILE_PATH = DATA_DIR / "app.log"

# Application Information
APP_NAME = "Resume Builder Pro"
APP_SUBTITLE = "Desktop AI-Ready Resume Builder"
APP_VERSION = "1.0.0"

# Editor & Autosave Configuration
AUTOSAVE_DELAY_MS = 1500  # Debounce delay in milliseconds

# Templates Configuration
DEFAULT_TEMPLATE = "modern"
SUPPORTED_TEMPLATES = {
    "modern": "Modern",
    "professional": "Professional",
    "minimal": "Minimal",
    "creative": "Creative",
}

# UI Theme Design System (Modern Neutral/Navy Palette)
THEME = {
    "primary": "#1E293B",        # Slate Dark Navy
    "primary_hover": "#0F172A",  # Darker Slate Navy
    "accent": "#2563EB",         # Royal Blue Accent
    "accent_hover": "#1D4ED8",   # Deep Blue Hover
    "bg_dark": "#0F172A",        # Left Sidebar Dark Background
    "bg_main": "#F8FAFC",        # Light neutral app workspace
    "card_bg": "#FFFFFF",        # Crisp White Container/Card Background
    "card_border": "#E2E8F0",    # Soft Gray Border
    "text_dark": "#0F172A",      # Primary Dark Text
    "text_muted": "#64748B",     # Muted Gray Subtitle Text
    "text_light": "#F8FAFC",     # Primary Light Text (Sidebar/Buttons)
    "danger": "#EF4444",         # Rose/Red Alert & Delete
    "danger_hover": "#DC2626",   # Dark Red Hover
    "success": "#10B981",        # Emerald Green Autosave/Status
    "warning": "#F59E0B",        # Amber Warning
    "font_family": "Segoe UI" if sys.platform == "win32" else "Helvetica",
}

# PDF Generator Default Settings
PDF_SETTINGS = {
    "page_size": "A4",
    "margin_top": 36,     # 0.5 inch
    "margin_bottom": 36,  # 0.5 inch
    "margin_left": 36,    # 0.5 inch
    "margin_right": 36,   # 0.5 inch
}

def ensure_directories() -> None:
    """Ensures that all required runtime directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
