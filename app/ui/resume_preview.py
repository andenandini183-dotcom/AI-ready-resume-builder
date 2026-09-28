"""
Live Real-Time Resume Preview Panel Component.
Renders structured resume data visually matching the selected template styling inside a scrollable canvas.
"""

import tkinter as tk
from typing import Optional, Dict, Any
from app.models.resume import Resume
from app.services.template_service import TemplateService
from app.config.settings import THEME


class ResumePreviewPanel(tk.Frame):
    """Scrollable live preview component rendering template layouts in real-time."""

    def __init__(self, parent: tk.Widget, template_service: Optional[TemplateService] = None):
        super().__init__(parent, bg="#CBD5E1", padx=16, pady=16)
        self.template_service = template_service or TemplateService()
        self.current_resume: Optional[Resume] = None

        self._build_ui()

    def _build_ui(self):
        # Outer Frame containing Canvas and Scrollbar
        canvas_frame = tk.Frame(self, bg="#CBD5E1")
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#CBD5E1", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)

        # White "Paper" Document Container (A4 aspect ratio frame)
        self.paper = tk.Frame(self.canvas, bg="#FFFFFF", padx=36, pady=36, width=640)
        self.paper.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.window_id = self.canvas.create_window((32, 20), window=self.paper, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_preview(self, resume: Resume):
        """Re-renders structured preview content for the active resume and template."""
        self.current_resume = resume

        # Clear existing paper content
        for widget in self.paper.winfo_children():
            widget.destroy()

        template = self.template_service.get_template(resume.template_name)
        data = template.render_structure(resume)

        primary_color = data["colors"]["primary"]
        secondary_color = data["colors"]["secondary"]
        accent_color = data["colors"]["accent"]

        # 1. Header
        header = data["header"]
        lbl_name = tk.Label(
            self.paper,
            text=header["name"],
            font=(THEME["font_family"], 18, "bold"),
            bg="#FFFFFF",
            fg=primary_color,
            anchor="center",
        )
        lbl_name.pack(fill="x")

        if header["title"]:
            lbl_title = tk.Label(
                self.paper,
                text=header["title"],
                font=(THEME["font_family"], 11, "bold"),
                bg="#FFFFFF",
                fg=accent_color,
                anchor="center",
            )
            lbl_title.pack(fill="x", pady=(2, 4))

        if header["contact_line"]:
            lbl_contact = tk.Label(
                self.paper,
                text=header["contact_line"],
                font=(THEME["font_family"], 8),
                bg="#FFFFFF",
                fg=secondary_color,
                anchor="center",
            )
            lbl_contact.pack(fill="x", pady=(0, 8))

        # Accent Divider Line
        div = tk.Frame(self.paper, bg=accent_color, height=2)
        div.pack(fill="x", pady=(0, 12))

        # 2. Professional Summary
        if data["summary"]:
            self._render_section_heading("PROFESSIONAL SUMMARY", primary_color)
            tk.Label(
                self.paper,
                text=data["summary"],
                font=(THEME["font_family"], 9),
                bg="#FFFFFF",
                fg=THEME["text_dark"],
                justify="left",
                wraplength=560,
                anchor="w",
            ).pack(fill="x", pady=(0, 10))

        # 3. Work Experience & Internships
        if data["experience"]:
            self._render_section_heading("WORK EXPERIENCE & INTERNSHIPS", primary_color)
            for exp in data["experience"]:
                exp_f = tk.Frame(self.paper, bg="#FFFFFF")
                exp_f.pack(fill="x", pady=(0, 8))

                hdr_line = tk.Frame(exp_f, bg="#FFFFFF")
                hdr_line.pack(fill="x")
                
                title_str = f"{exp['position']} — {exp['company']}" if exp['position'] and exp['company'] else (exp['position'] or exp['company'])
                if exp['location']:
                    title_str += f" ({exp['location']})"
                    
                tk.Label(hdr_line, text=title_str, font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side="left")
                tk.Label(hdr_line, text=exp['date_range'], font=(THEME["font_family"], 8), bg="#FFFFFF", fg=secondary_color).pack(side="right")

                for resp in exp['responsibilities']:
                    tk.Label(
                        exp_f,
                        text=f"• {resp}",
                        font=(THEME["font_family"], 8),
                        bg="#FFFFFF",
                        fg=THEME["text_dark"],
                        justify="left",
                        wraplength=540,
                        anchor="w",
                    ).pack(fill="x", padx=(10, 0), pady=1)

                for ach in exp['achievements']:
                    tk.Label(
                        exp_f,
                        text=f"• Key Achievement: {ach}",
                        font=(THEME["font_family"], 8, "bold"),
                        bg="#FFFFFF",
                        fg=THEME["text_dark"],
                        justify="left",
                        wraplength=540,
                        anchor="w",
                    ).pack(fill="x", padx=(10, 0), pady=1)

        # 4. Education
        if data["education"]:
            self._render_section_heading("EDUCATION", primary_color)
            for edu in data["education"]:
                edu_f = tk.Frame(self.paper, bg="#FFFFFF")
                edu_f.pack(fill="x", pady=(0, 6))

                hdr_line = tk.Frame(edu_f, bg="#FFFFFF")
                hdr_line.pack(fill="x")

                deg_str = f"{edu['degree']} — {edu['institution']}" if edu['degree'] else edu['institution']
                if edu['gpa']:
                    deg_str += f" | {edu['gpa']}"
                    
                tk.Label(hdr_line, text=deg_str, font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side="left")
                tk.Label(hdr_line, text=edu['date_range'], font=(THEME["font_family"], 8), bg="#FFFFFF", fg=secondary_color).pack(side="right")

                if edu['description']:
                    tk.Label(edu_f, text=edu['description'], font=(THEME["font_family"], 8), bg="#FFFFFF", fg=THEME["text_dark"], justify="left", anchor="w").pack(fill="x", pady=1)

        # 5. Key Projects
        if data["projects"]:
            self._render_section_heading("KEY PROJECTS", primary_color)
            for proj in data["projects"]:
                p_f = tk.Frame(self.paper, bg="#FFFFFF")
                p_f.pack(fill="x", pady=(0, 4))

                hdr_line = tk.Frame(p_f, bg="#FFFFFF")
                hdr_line.pack(fill="x")

                p_str = proj['name']
                tk.Label(hdr_line, text=p_str, font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side="left")
                if proj['date_range']:
                    tk.Label(hdr_line, text=proj['date_range'], font=(THEME["font_family"], 8), bg="#FFFFFF", fg=secondary_color).pack(side="right")

                for c in proj['contributions']:
                    tk.Label(
                        p_f,
                        text=f"• {c}",
                        font=(THEME["font_family"], 8),
                        bg="#FFFFFF",
                        fg=THEME["text_dark"],
                        justify="left",
                        wraplength=540,
                        anchor="w",
                    ).pack(fill="x", padx=(10, 0), pady=1)

        # 6. Technical Skills & Competencies
        if data["skills"]:
            self._render_section_heading("TECHNICAL SKILLS & COMPETENCIES", primary_color)
            for cat, items in data["skills"].items():
                s_str = f"{cat}: " + ", ".join(items)
                tk.Label(
                    self.paper,
                    text=s_str,
                    font=(THEME["font_family"], 8),
                    bg="#FFFFFF",
                    fg=THEME["text_dark"],
                    justify="left",
                    wraplength=560,
                    anchor="w",
                ).pack(fill="x", pady=1)

        # 7. Certifications & Licenses
        if data["certifications"]:
            self._render_section_heading("CERTIFICATIONS & LICENSES", primary_color)
            for cert in data["certifications"]:
                c_f = tk.Frame(self.paper, bg="#FFFFFF")
                c_f.pack(fill="x", pady=(0, 2))

                c_name = cert['name'].strip()
                if c_name.lower() == "achievements":
                    tk.Label(c_f, text="Achievements", font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side="left", pady=(4, 2))
                else:
                    c_str = f"• {c_name} — {cert['organization']}" if cert['organization'] else f"• {c_name}"
                    tk.Label(c_f, text=c_str, font=(THEME["font_family"], 8), bg="#FFFFFF", fg=THEME["text_dark"]).pack(side="left")
                    if cert['date']:
                        tk.Label(c_f, text=cert['date'], font=(THEME["font_family"], 8), bg="#FFFFFF", fg=secondary_color).pack(side="right")

    def _render_section_heading(self, text: str, color: str):
        tk.Label(
            self.paper,
            text=text,
            font=(THEME["font_family"], 10, "bold"),
            bg="#FFFFFF",
            fg=color,
            anchor="w",
        ).pack(fill="x", pady=(6, 1))
        div = tk.Frame(self.paper, bg="#E2E8F0", height=1)
        div.pack(fill="x", pady=(0, 4))
