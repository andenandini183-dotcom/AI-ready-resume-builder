"""
ReportLab PDF Document Generator.
Converts structured resume data and template styling into clean, single-page A4 PDF documents.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

from app.models.resume import Resume
from app.services.template_service import TemplateService
from app.utils.formatting import clean_garbage_text, re_strip_bullet_prefix
from app.utils.logger import logger


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to add page footer to PDF documents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 18, 8, page_text)
        self.restoreState()


class PDFGenerator:
    """Generates professional single-page PDF resumes using ReportLab."""

    def __init__(self, template_service: Optional[TemplateService] = None):
        self.template_service = template_service or TemplateService()

    def generate(self, resume: Resume, output_path: Path) -> Path:
        """Renders resume to a 1-page PDF file at output_path."""
        template = self.template_service.get_template(resume.template_name)
        data = template.render_structure(resume)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=18,
            rightMargin=18,
            topMargin=16,
            bottomMargin=16,
        )

        styles = getSampleStyleSheet()
        primary_hex = data["colors"]["primary"]
        secondary_hex = data["colors"]["secondary"]
        accent_hex = data["colors"]["accent"]

        content_width = 559.27
        col1_w = 425.0
        col2_w = 134.27

        # Custom Paragraph Styles
        name_style = ParagraphStyle(
            "DocName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=19,
            textColor=colors.HexColor(primary_hex),
            alignment=TA_CENTER if data["layout_style"] != "creative_sidebar" else TA_LEFT,
        )

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11.5,
            textColor=colors.HexColor(accent_hex),
            alignment=TA_CENTER if data["layout_style"] != "creative_sidebar" else TA_LEFT,
            spaceAfter=1,
        )

        contact_style = ParagraphStyle(
            "DocContact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor(secondary_hex),
            alignment=TA_CENTER if data["layout_style"] != "creative_sidebar" else TA_LEFT,
            spaceAfter=3,
        )

        section_heading_style = ParagraphStyle(
            "DocSectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=11.5,
            textColor=colors.HexColor(primary_hex),
            spaceBefore=3,
            spaceAfter=1,
        )

        item_title_style = ParagraphStyle(
            "DocItemTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=10.5,
            textColor=colors.HexColor("#0F172A"),
        )

        item_sub_style = ParagraphStyle(
            "DocItemSub",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor(secondary_hex),
        )

        date_style = ParagraphStyle(
            "DocItemDate",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor(secondary_hex),
            alignment=TA_RIGHT,
        )

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#334155"),
            alignment=TA_LEFT,
            spaceAfter=1.5,
        )

        bullet_style = ParagraphStyle(
            "DocBullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#334155"),
            leftIndent=8,
            spaceAfter=1,
        )

        story: List[Any] = []

        # 1. Header Section
        header = data["header"]
        story.append(Paragraph(clean_garbage_text(header["name"]), name_style))
        if header["title"]:
            story.append(Paragraph(clean_garbage_text(header["title"]), title_style))
        if header["contact_line"]:
            story.append(Paragraph(clean_garbage_text(header["contact_line"]), contact_style))

        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(accent_hex), spaceBefore=1, spaceAfter=3))

        # 2. Professional Summary
        if data["summary"]:
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=2))
            story.append(Paragraph(clean_garbage_text(data["summary"]), body_style))
            story.append(Spacer(1, 2))

        # 3. Work Experience & Internships
        if data["experience"]:
            story.append(Paragraph("WORK EXPERIENCE & INTERNSHIPS", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=2))

            for exp in data["experience"]:
                exp_blocks = []
                pos = clean_garbage_text(exp['position'])
                comp = clean_garbage_text(exp['company'])
                col1_text = f"<b>{pos}</b> — {comp}" if pos and comp else (f"<b>{pos}</b>" if pos else comp)
                if exp['location']:
                    col1_text += f" ({clean_garbage_text(exp['location'])})"

                t_data = [
                    [Paragraph(col1_text, item_title_style), Paragraph(exp['date_range'], date_style)]
                ]
                t = Table(t_data, colWidths=[col1_w, col2_w])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                ]))
                exp_blocks.append(t)

                for b in exp["responsibilities"]:
                    clean_b = re_strip_bullet_prefix(clean_garbage_text(b))
                    if clean_b:
                        exp_blocks.append(Paragraph(f"• {clean_b}", bullet_style))

                for a in exp["achievements"]:
                    clean_a = re_strip_bullet_prefix(clean_garbage_text(a))
                    if clean_a:
                        exp_blocks.append(Paragraph(f"• Key Achievement: {clean_a}", bullet_style))

                exp_blocks.append(Spacer(1, 1.5))
                story.append(KeepTogether(exp_blocks))

            story.append(Spacer(1, 1.5))

        # 4. Education
        if data["education"]:
            story.append(Paragraph("EDUCATION", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=2))

            for edu in data["education"]:
                edu_blocks = []
                deg = clean_garbage_text(edu['degree'])
                inst = clean_garbage_text(edu['institution'])
                col1_text = f"<b>{deg}</b> — {inst}" if deg else inst
                if edu['gpa']:
                    col1_text += f" | {clean_garbage_text(edu['gpa'])}"

                t_data = [
                    [Paragraph(col1_text, item_title_style), Paragraph(edu['date_range'], date_style)]
                ]
                t = Table(t_data, colWidths=[col1_w, col2_w])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                ]))
                edu_blocks.append(t)
                if edu['description']:
                    edu_blocks.append(Paragraph(clean_garbage_text(edu['description']), body_style))
                edu_blocks.append(Spacer(1, 1.5))
                story.append(KeepTogether(edu_blocks))

            story.append(Spacer(1, 1.5))

        # 5. Key Projects
        if data["projects"]:
            story.append(Paragraph("KEY PROJECTS", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=2))

            for proj in data["projects"]:
                proj_blocks = []
                p_name = clean_garbage_text(proj['name'])
                title_line = f"<b>{p_name}</b>"

                t_data = [
                    [Paragraph(title_line, item_title_style), Paragraph(proj['date_range'], date_style)]
                ]
                t = Table(t_data, colWidths=[col1_w, col2_w])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                ]))
                proj_blocks.append(t)

                for c in proj['contributions']:
                    clean_c = re_strip_bullet_prefix(clean_garbage_text(c))
                    if clean_c:
                        proj_blocks.append(Paragraph(f"• {clean_c}", bullet_style))

                if proj['url']:
                    proj_blocks.append(Paragraph(f"Link: <a href='{proj['url']}' color='{accent_hex}'>{proj['url']}</a>", item_sub_style))

                proj_blocks.append(Spacer(1, 1.5))
                story.append(KeepTogether(proj_blocks))

            story.append(Spacer(1, 1.5))

        # 6. Technical Skills & Competencies
        if data["skills"]:
            story.append(Paragraph("TECHNICAL SKILLS & COMPETENCIES", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=2))

            skill_lines = []
            for cat, items in data["skills"].items():
                cat_clean = clean_garbage_text(cat)
                items_clean = [re_strip_bullet_prefix(clean_garbage_text(it)) for it in items if clean_garbage_text(it)]
                if items_clean:
                    items_str = ", ".join(items_clean)
                    skill_lines.append(Paragraph(f"<b>{cat_clean}:</b> {items_str}", body_style))

            if skill_lines:
                story.append(KeepTogether(skill_lines))
                story.append(Spacer(1, 1.5))

        # 7. Certifications & Licenses
        if data["certifications"]:
            story.append(Paragraph("CERTIFICATIONS & LICENSES", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=2))

            cert_blocks = []
            for cert in data["certifications"]:
                c_name = re_strip_bullet_prefix(clean_garbage_text(cert['name']))
                c_org = clean_garbage_text(cert['organization'])
                
                if c_name.lower() == "achievements":
                    cert_blocks.append(Spacer(1, 1.5))
                    cert_blocks.append(Paragraph("<b>Achievements</b>", body_style))
                else:
                    cert_line = f"• <b>{c_name}</b>"
                    if c_org:
                        cert_line += f" — {c_org}"
                    if cert['credential_id']:
                        cert_line += f" (ID: {clean_garbage_text(cert['credential_id'])})"
                    cert_blocks.append(Paragraph(cert_line, bullet_style))

            story.append(KeepTogether(cert_blocks))
            story.append(Spacer(1, 1))

        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info(f"PDF generated successfully at {output_path}")
        return output_path


