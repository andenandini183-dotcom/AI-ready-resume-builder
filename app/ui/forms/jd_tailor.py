"""
Job Description Resume Builder & Tailoring View.
Allows users to provide their base resume details (paste, file upload, or select active)
and a target Job Description, then BUILDS a brand new tailored resume with ATS scoring and instant PDF export.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional

from app.models.resume import Resume
from app.services.resume_service import ResumeService
from app.config.settings import THEME
from app.ui.components.buttons import create_button
from app.utils.file_utils import format_resume_to_text


class JDTailorForm(tk.Frame):
    """UI Panel for Building a Tailored Resume from Job Description + Candidate Resume."""

    def __init__(
        self,
        parent: tk.Widget,
        resume: Resume,
        resume_service: ResumeService,
        on_data_changed: Callable[[], None],
        on_open_resume: Optional[Callable[[Resume], None]] = None,
    ):
        super().__init__(parent, bg="#FFFFFF", padx=24, pady=24)
        self.resume = resume
        self.resume_service = resume_service
        self.on_data_changed = on_data_changed
        self.on_open_resume = on_open_resume

        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#FFFFFF")
        hdr.pack(fill="x", pady=(0, 16))

        title_frame = tk.Frame(hdr, bg="#FFFFFF")
        title_frame.pack(side="left")

        tk.Label(
            title_frame,
            text="Build Resume from Job Description",
            font=(THEME["font_family"], 14, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Provide your base resume details and target job description to build a new tailored resume with ATS score and PDF export.",
            font=(THEME["font_family"], 9),
            bg="#FFFFFF",
            fg=THEME["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Main Split Grid (Base Resume Input Left | Job Description Input Right)
        grid_frame = tk.Frame(self, bg="#FFFFFF")
        grid_frame.pack(fill="x", pady=(0, 16))
        grid_frame.columnconfigure(0, weight=1, pad=12)
        grid_frame.columnconfigure(1, weight=1, pad=12)

        # LEFT COLUMN: Candidate Base Resume Input
        left_col = tk.Frame(grid_frame, bg="#FFFFFF")
        left_col.grid(row=0, column=0, sticky="nsew")

        lbl_res_hdr = tk.Frame(left_col, bg="#FFFFFF")
        lbl_res_hdr.pack(fill="x", pady=(0, 4))

        tk.Label(
            lbl_res_hdr,
            text="1. User Resume Details *",
            font=(THEME["font_family"], 10, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        ).pack(side="left")

        btn_upload = tk.Button(
            lbl_res_hdr,
            text="📁 Upload File",
            command=self._upload_resume_file,
            bg="#F1F5F9",
            fg=THEME["text_dark"],
            font=(THEME["font_family"], 8, "bold"),
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
        )
        btn_upload.pack(side="right")

        self.txt_resume = tk.Text(
            left_col,
            font=(THEME["font_family"], 9),
            bg="#F8FAFC",
            fg=THEME["text_dark"],
            bd=1,
            relief="solid",
            height=8,
            wrap="word",
        )
        self.txt_resume.pack(fill="both", expand=True)

        initial_resume_text = format_resume_to_text(self.resume)
        if not initial_resume_text or len(initial_resume_text) < 30:
            initial_resume_text = "Nandini Ande\nandenandini183@gmail.com | 7995970147\n\nSUMMARY:\nMotivated student specializing in Artificial Intelligence and Machine Learning.\n\nWORK EXPERIENCE:\nAI Developer Intern — Tech Startup\n- Developed ML models and APIs using Python and FastAPI.\n\nEDUCATION:\nB.Tech in AI & ML — University\n\nSKILLS:\nPython, Java, React.js, Flask, FastAPI, MongoDB, AI, Machine Learning, NLP"

        self.txt_resume.insert("1.0", initial_resume_text)

        # RIGHT COLUMN: Target Job Description Input
        right_col = tk.Frame(grid_frame, bg="#FFFFFF")
        right_col.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            right_col,
            text="2. Target Job Description *",
            font=(THEME["font_family"], 10, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        ).pack(anchor="w", pady=(0, 4))

        self.txt_jd = tk.Text(
            right_col,
            font=(THEME["font_family"], 9),
            bg="#F8FAFC",
            fg=THEME["text_dark"],
            bd=1,
            relief="solid",
            height=8,
            wrap="word",
        )
        self.txt_jd.pack(fill="both", expand=True)
        self.txt_jd.insert(
            "1.0",
            "Senior Software Engineer\nWe are looking for a Senior Software Engineer with strong experience in Python, Software, APIs, Architecture, Cloud, and Docker. Leadership and microservices experience preferred.",
        )

        # Action Button Row (BUILD RESUME & EXPORT PDF)
        btn_bar = tk.Frame(self, bg="#FFFFFF")
        btn_bar.pack(fill="x", pady=16)

        btn_build = create_button(
            btn_bar,
            "⚡ BUILD TAILORED RESUME & EXPORT PDF",
            self._build_tailored_resume_action,
            style_type="primary",
        )
        btn_build.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_analyze_only = create_button(
            btn_bar,
            "🔍 Analyze ATS Score Only",
            self._analyze_ats_only,
            style_type="outline",
        )
        btn_analyze_only.pack(side="right")

        # Results & Insights Output Container
        self.results_frame = tk.Frame(self, bg="#F8FAFC", bd=1, relief="solid", padx=16, pady=16)
        self.results_frame.pack(fill="x", pady=16)

        self._render_empty_results()

    def _render_empty_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.results_frame,
            text="Provide candidate details and target Job Description above, then click '⚡ BUILD TAILORED RESUME & EXPORT PDF'.",
            font=(THEME["font_family"], 9, "italic"),
            bg="#F8FAFC",
            fg=THEME["text_muted"],
        ).pack(pady=20)

    def _upload_resume_file(self):
        file_path = filedialog.askopenfilename(
            title="Upload Resume File",
            filetypes=[("Supported Resume Files", "*.pdf;*.json;*.txt"), ("PDF Files (*.pdf)", "*.pdf"), ("JSON Files (*.json)", "*.json"), ("Text Files (*.txt)", "*.txt"), ("All Files", "*.*")],
        )
        if file_path:
            try:
                imported = self.resume_service.import_resume(file_path)
                self.resume = imported
                self.txt_resume.delete("1.0", tk.END)
                
                content = format_resume_to_text(imported)
                self.txt_resume.insert("1.0", content)
                
                messagebox.showinfo("Resume Uploaded", f"Successfully loaded resume details from:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Upload Error", f"Could not read resume file: {e}")

    def _build_tailored_resume_action(self):
        resume_text = self.txt_resume.get("1.0", tk.END).strip()
        jd_text = self.txt_jd.get("1.0", tk.END).strip()

        if not resume_text:
            messagebox.showwarning("Missing Input", "Please enter or upload user resume details.")
            return

        if not jd_text:
            messagebox.showwarning("Missing Input", "Please enter the target Job Description.")
            return

        # Build brand new tailored resume
        new_resume, jd_result = self.resume_service.build_new_resume_from_jd(
            base_input=resume_text if len(resume_text) > 50 else self.resume,
            job_description=jd_text,
        )

        # Update active resume reference
        self.resume = new_resume
        self.on_data_changed()
        self._display_results(jd_result, is_newly_built=True)

        # Generate & Export PDF immediately
        try:
            pdf_path = self.resume_service.export_pdf(new_resume, open_after=True)
            messagebox.showinfo(
                "Resume Built & Exported!",
                f"🎉 Successfully built tailored resume for '{jd_result.job_title_detected}' with ATS Score: {jd_result.score}%!\n\nExported PDF:\n{pdf_path}",
            )
        except Exception as e:
            messagebox.showerror("PDF Export Warning", f"Resume built successfully, but PDF export encountered an issue: {e}")

    def _analyze_ats_only(self):
        jd_text = self.txt_jd.get("1.0", tk.END).strip()
        if not jd_text:
            messagebox.showwarning("Missing Input", "Please enter the target Job Description.")
            return

        res = self.resume_service.analyze_jd_match(self.resume, jd_text)
        self._display_results(res, is_newly_built=False)

    def _display_results(self, res, is_newly_built: bool = False):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Score & Status Badge Row
        badge_frame = tk.Frame(self.results_frame, bg="#F8FAFC")
        badge_frame.pack(fill="x", pady=(0, 12))

        score_color = THEME["success"] if res.score >= 70 else (THEME["warning"] if res.score >= 50 else THEME["danger"])

        lbl_score = tk.Label(
            badge_frame,
            text=f"ATS MATCH SCORE: {res.score}%",
            font=(THEME["font_family"], 15, "bold"),
            bg="#F8FAFC",
            fg=score_color,
        )
        lbl_score.pack(side="left")

        if is_newly_built:
            lbl_built = tk.Label(
                badge_frame,
                text="✨ TAILORED RESUME CREATED & SAVED",
                font=(THEME["font_family"], 9, "bold"),
                bg="#ECFDF5",
                fg=THEME["success"],
                padx=8,
                pady=4,
            )
            lbl_built.pack(side="right")

        # Action buttons in report frame
        action_row = tk.Frame(self.results_frame, bg="#F8FAFC")
        action_row.pack(fill="x", pady=(0, 12))

        create_button(
            action_row,
            "📄 Export Resume PDF Again",
            lambda: self.resume_service.export_pdf(self.resume, open_after=True),
            style_type="primary",
        ).pack(side="left", padx=(0, 8))

        if self.on_open_resume:
            create_button(
                action_row,
                "✏️ Edit Built Resume in Editor",
                lambda: self.on_open_resume(self.resume),
                style_type="outline",
            ).pack(side="left")

        # Matched Keywords
        tk.Label(
            self.results_frame,
            text="✅ Matched Target Keywords",
            font=(THEME["font_family"], 10, "bold"),
            bg="#F8FAFC",
            fg=THEME["success"],
        ).pack(anchor="w", pady=(4, 2))

        matched_str = ", ".join(res.matched_keywords) if res.matched_keywords else "None matched yet."
        tk.Label(
            self.results_frame,
            text=matched_str,
            font=(THEME["font_family"], 9),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
            wraplength=550,
            justify="left",
            padx=8,
            pady=6,
            bd=1,
            relief="solid",
        ).pack(anchor="w", fill="x", pady=(0, 8))

        # Missing Keywords
        if res.missing_keywords:
            tk.Label(
                self.results_frame,
                text="📌 Integrated & Recommended Target Keywords",
                font=(THEME["font_family"], 10, "bold"),
                bg="#F8FAFC",
                fg=THEME["accent"],
            ).pack(anchor="w", pady=(4, 2))

            missing_str = ", ".join(res.missing_keywords)
            tk.Label(
                self.results_frame,
                text=missing_str,
                font=(THEME["font_family"], 9),
                bg="#FFFFFF",
                fg=THEME["text_dark"],
                wraplength=550,
                justify="left",
                padx=8,
                pady=6,
                bd=1,
                relief="solid",
            ).pack(anchor="w", fill="x", pady=(0, 8))
