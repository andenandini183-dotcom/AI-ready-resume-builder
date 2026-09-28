"""
Main Application Window Container.
Orchestrates Tkinter root window, view transitions, autosave debounce timer, and service integration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any

from app.models.resume import Resume
from app.services.resume_service import ResumeService
from app.config.settings import APP_NAME, AUTOSAVE_DELAY_MS, THEME
from app.ui.dashboard import DashboardView
from app.ui.components.navbar import Navbar
from app.ui.components.sidebar import Sidebar
from app.ui.components.dialogs import PromptDialog, ConfirmDialog, ATSReportDialog
from app.ui.forms.personal_info import PersonalInfoForm
from app.ui.forms.education import EducationForm
from app.ui.forms.experience import ExperienceForm
from app.ui.forms.projects import ProjectsForm
from app.ui.forms.skills import SkillsForm
from app.ui.forms.certifications import CertificationsForm
from app.ui.forms.jd_tailor import JDTailorForm
from app.ui.resume_preview import ResumePreviewPanel


class MainWindow:
    """Root Application Window Container."""

    def __init__(self, resume_service: Optional[ResumeService] = None):
        self.resume_service = resume_service or ResumeService()

        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1240x780")
        self.root.minsize(1000, 650)
        self.root.configure(bg=THEME["bg_main"])

        self.current_resume: Optional[Resume] = None
        self.active_section: str = "personal_info"
        self.autosave_job: Optional[str] = None

        self._configure_ttk_styles()
        self._build_main_container()
        self.show_dashboard()

    def _configure_ttk_styles(self):
        """Sets up custom TTK widget styling."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=THEME["bg_main"])
        style.configure("TLabel", background=THEME["bg_main"], foreground=THEME["text_dark"], font=(THEME["font_family"], 9))

    def _build_main_container(self):
        """Creates root view container frame."""
        self.container = tk.Frame(self.root, bg=THEME["bg_main"])
        self.container.pack(fill="both", expand=True)

    def show_dashboard(self):
        """Switches view to the main Dashboard."""
        self._cancel_autosave()
        self._clear_container()

        self.dashboard_view = DashboardView(
            self.container,
            resume_service=self.resume_service,
            on_open_resume=self.open_editor,
        )
        self.dashboard_view.pack(fill="both", expand=True)

    def open_editor(self, resume: Resume):
        """Switches view to the Resume Editor interface."""
        if not resume or not resume.id:
            return
            
        self.current_resume = self.resume_service.get_resume(resume.id) or resume
        self.active_section = "personal_info"
        self._clear_container()
        self._build_editor_ui()

    def _build_editor_ui(self):
        if not self.current_resume:
            return

        # 1. Top Navbar
        self.navbar = Navbar(
            self.container,
            resume_title=self.current_resume.title,
            on_back=self.show_dashboard,
            on_title_click=self._edit_resume_title,
            on_export=self._export_pdf,
            on_save=self._force_save,
        )
        self.navbar.pack(fill="x", side="top")

        # Main Body (Sidebar + Content Workspace + Live Preview Split)
        body = tk.Frame(self.container, bg=THEME["bg_main"])
        body.pack(fill="both", expand=True)

        # 2. Left Sidebar
        self.sidebar = Sidebar(
            body,
            on_section_change=self._on_section_changed,
            active_section=self.active_section,
        )
        self.sidebar.pack(side="left", fill="y")

        # 3. Form Editor Workspace Frame (Center)
        self.editor_workspace = tk.Frame(body, bg="#FFFFFF", bd=1, relief="solid")
        self.editor_workspace.pack(side="left", fill="both", expand=True)

        # 4. Live Preview Panel (Right)
        self.preview_panel = ResumePreviewPanel(body, template_service=self.resume_service.template_service)
        self.preview_panel.pack(side="right", fill="both", expand=True)

        # Render Active Section Form & Initial Preview
        self._render_active_section_form()
        self.preview_panel.update_preview(self.current_resume)

    def _render_active_section_form(self):
        """Displays form associated with the currently selected sidebar section."""
        for widget in self.editor_workspace.winfo_children():
            widget.destroy()

        if not self.current_resume:
            return

        section = self.active_section

        if section == "personal_info":
            form = PersonalInfoForm(self.editor_workspace, self.current_resume.personal_info, on_change=self._on_data_changed)
            form.pack(fill="both", expand=True)
        elif section == "education":
            form = EducationForm(self.editor_workspace, self.current_resume.education, on_change=self._on_data_changed)
            form.pack(fill="both", expand=True)
        elif section == "experience":
            form = ExperienceForm(self.editor_workspace, self.current_resume.experience, on_change=self._on_data_changed)
            form.pack(fill="both", expand=True)
        elif section == "projects":
            form = ProjectsForm(self.editor_workspace, self.current_resume.projects, on_change=self._on_data_changed)
            form.pack(fill="both", expand=True)
        elif section == "skills":
            form = SkillsForm(self.editor_workspace, self.current_resume.skills, on_change=self._on_data_changed)
            form.pack(fill="both", expand=True)
        elif section == "certifications":
            form = CertificationsForm(self.editor_workspace, self.current_resume.certifications, on_change=self._on_data_changed)
            form.pack(fill="both", expand=True)
        elif section == "jd_tailor":
            form = JDTailorForm(
                self.editor_workspace,
                self.current_resume,
                self.resume_service,
                on_data_changed=self._on_data_changed,
                on_open_resume=self.open_editor,
            )
            form.pack(fill="both", expand=True)
        elif section == "preview":
            lbl = tk.Label(
                self.editor_workspace,
                text="Live Preview is active on the right panel.\nAny edits automatically update your preview!",
                font=(THEME["font_family"], 11),
                bg="#FFFFFF",
                fg=THEME["text_muted"],
                padx=30,
                pady=40,
            )
            lbl.pack()
        elif section == "templates":
            self._render_template_selector_form()
        elif section == "ats_analysis":
            self._run_ats_analysis()
        elif section == "export":
            self._export_pdf()

    def _render_template_selector_form(self):
        """Renders interactive Template Selection panel."""
        f = tk.Frame(self.editor_workspace, bg="#FFFFFF", padx=24, pady=24)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Choose Template", font=(THEME["font_family"], 14, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(f, text="Select a professional visual template for your resume.", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w", pady=(2, 16))

        templates = self.resume_service.template_service.get_all_templates()
        for t in templates:
            card = tk.Frame(f, bg="#FFFFFF", bd=1, relief="solid", padx=16, pady=12)
            card.pack(fill="x", pady=6)

            info_f = tk.Frame(card, bg="#FFFFFF")
            info_f.pack(side="left")

            is_active = self.current_resume and self.current_resume.template_name == t.name
            title_text = f"{t.display_name} {'(Active)' if is_active else ''}"

            tk.Label(info_f, text=title_text, font=(THEME["font_family"], 10, "bold"), bg="#FFFFFF", fg=THEME["accent"] if is_active else THEME["text_dark"]).pack(anchor="w")
            tk.Label(info_f, text=t.description, font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

            if not is_active:
                btn = tk.Button(
                    card,
                    text="Use Template",
                    command=lambda name=t.name: self._switch_template(name),
                    bg=THEME["accent"],
                    fg="#FFFFFF",
                    font=(THEME["font_family"], 9, "bold"),
                    relief="flat",
                    bd=0,
                    padx=12,
                    pady=4,
                    cursor="hand2",
                )
                btn.pack(side="right")

    def _switch_template(self, template_name: str):
        if self.current_resume:
            self.current_resume.template_name = template_name
            self._on_data_changed()
            self._render_template_selector_form()

    def _on_section_changed(self, section_key: str):
        self.active_section = section_key
        self._render_active_section_form()

    def _on_data_changed(self):
        """Handler called when form data is modified by user."""
        if not self.current_resume:
            return

        # Update Live Preview
        self.preview_panel.update_preview(self.current_resume)

        # Schedule Delayed Autosave
        if hasattr(self, "navbar"):
            self.navbar.set_status("Saving...")
        self._schedule_autosave()

    def _schedule_autosave(self):
        self._cancel_autosave()
        self.autosave_job = self.root.after(AUTOSAVE_DELAY_MS, self._perform_autosave)

    def _cancel_autosave(self):
        if self.autosave_job:
            self.root.after_cancel(self.autosave_job)
            self.autosave_job = None

    def _perform_autosave(self):
        if self.current_resume and self.current_resume.id:
            self.resume_service.update_resume(self.current_resume)
            if hasattr(self, "navbar"):
                self.navbar.set_status("Saved")

    def _force_save(self):
        self._cancel_autosave()
        self._perform_autosave()

    def _edit_resume_title(self):
        if not self.current_resume:
            return
        dlg = PromptDialog(self.root, "Rename Resume", "Enter new resume title:", self.current_resume.title)
        if dlg.result:
            self.current_resume.title = dlg.result
            self.navbar.update_title(self.current_resume.title)
            self._on_data_changed()

    def _run_ats_analysis(self):
        if self.current_resume:
            self._force_save()
            result = self.resume_service.analyze_ats(self.current_resume)
            ATSReportDialog(self.root, result)

    def _export_pdf(self):
        if self.current_resume:
            self._force_save()
            try:
                pdf_path = self.resume_service.export_pdf(self.current_resume, open_after=True)
                messagebox.showinfo("Export Successful", f"Resume PDF exported successfully to:\n{pdf_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export PDF: {e}")

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def run(self):
        """Starts Tkinter mainloop execution."""
        self.root.mainloop()
