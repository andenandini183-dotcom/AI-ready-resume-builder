"""
Export Service.
Handles exporting resumes to PDF format, opening PDFs, and determining default output file paths.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from app.models.resume import Resume
from app.services.pdf_generator import PDFGenerator
from app.config.settings import OUTPUT_DIR, ensure_directories
from app.utils.file_utils import sanitize_filename
from app.utils.logger import logger


class ExportService:
    """Manages PDF document exports and system viewer integration."""

    def __init__(self, pdf_generator: Optional[PDFGenerator] = None):
        self.pdf_generator = pdf_generator or PDFGenerator()

    def generate_default_filepath(self, resume: Resume) -> Path:
        """Generates standard output file path (e.g. output/generated_resumes/John_Doe_Resume.pdf)."""
        ensure_directories()
        name_part = resume.personal_info.full_name or resume.title or "Resume"
        safe_name = sanitize_filename(f"{name_part}_Resume")
        return OUTPUT_DIR / f"{safe_name}.pdf"

    def export_pdf(self, resume: Resume, target_path: Optional[Path] = None) -> Path:
        """Generates PDF resume file at target path or default path."""
        file_path = target_path or self.generate_default_filepath(resume)
        return self.pdf_generator.generate(resume, file_path)

    def open_pdf_in_system_viewer(self, file_path: Path) -> bool:
        """Opens generated PDF in the default operating system PDF viewer."""
        if not file_path.exists():
            logger.error(f"Cannot open PDF. File does not exist: {file_path}")
            return False

        try:
            if sys.platform == "win32":
                os.startfile(str(file_path))  # type: ignore
            elif sys.platform == "darwin":
                subprocess.run(["open", str(file_path)], check=True)
            else:
                subprocess.run(["xdg-open", str(file_path)], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to open PDF viewer for {file_path}: {e}")
            return False
