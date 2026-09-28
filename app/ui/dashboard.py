"""
Application Dashboard View.
Displays resume cards, search bar, creation CTA, and empty states.
"""

import tkinter as tk
from typing import Callable, List, Optional
from app.models.resume import Resume
from app.services.resume_service import ResumeService
from app.config.settings import THEME
from app.ui.components.buttons import create_button
from app.ui.components.dialogs import PromptDialog, ConfirmDialog


class DashboardView(tk.Frame):
    """Main Dashboard View displaying user resumes."""

    def __init__(
        self,
        parent: tk.Widget,
        resume_service: ResumeService,
        on_open_resume: Callable[[Resume], None],
    ):
        super().__init__(parent, bg=THEME["bg_main"], padx=32, pady=28)
        self.resume_service = resume_service
        self.on_open_resume = on_open_resume

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Header Frame
        hdr_frame = tk.Frame(self, bg=THEME["bg_main"])
        hdr_frame.pack(fill="x", pady=(0, 24))

        left_hdr = tk.Frame(hdr_frame, bg=THEME["bg_main"])
        left_hdr.pack(side="left")

        lbl_title = tk.Label(
            left_hdr,
            text="Resume Builder",
            font=(THEME["font_family"], 20, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            left_hdr,
            text="Create, manage, and optimize your professional resumes.",
            font=(THEME["font_family"], 10),
            bg=THEME["bg_main"],
            fg=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        right_hdr = tk.Frame(hdr_frame, bg=THEME["bg_main"])
        right_hdr.pack(side="right")

        btn_build_jd = create_button(
            right_hdr,
            "✨ Build Resume from JD",
            self._build_from_jd_action,
            style_type="secondary",
        )
        btn_build_jd.pack(side="left", padx=(0, 8))

        btn_create = create_button(
            right_hdr,
            "+ Create New Resume",
            self._create_new_resume,
            style_type="primary",
        )
        btn_create.pack(side="left")

        # 2. Controls Frame (Search Bar)
        ctrl_frame = tk.Frame(self, bg=THEME["bg_main"])
        ctrl_frame.pack(fill="x", pady=(0, 16))

        tk.Label(
            ctrl_frame,
            text="Search:",
            font=(THEME["font_family"], 9, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["text_dark"],
        ).pack(side="left", padx=(0, 8))

        self.entry_search = tk.Entry(
            ctrl_frame,
            font=(THEME["font_family"], 9),
            bg="#FFFFFF",
            bd=1,
            relief="solid",
            width=32,
        )
        self.entry_search.pack(side="left", ipady=4)
        self.entry_search.bind("<KeyRelease>", self._on_search)

        # 3. Resume List Container
        self.list_container = tk.Frame(self, bg=THEME["bg_main"])
        self.list_container.pack(fill="both", expand=True)

    def refresh(self, query: str = ""):
        """Reloads resume list from repository."""
        for widget in self.list_container.winfo_children():
            widget.destroy()

        resumes = self.resume_service.search_resumes(query)

        if not resumes:
            self._render_empty_state(query)
            return

        for resume in resumes:
            self._render_resume_card(resume)

    def _render_empty_state(self, query: str):
        empty_frame = tk.Frame(self.list_container, bg="#FFFFFF", bd=1, relief="solid", padx=32, pady=40)
        empty_frame.pack(fill="x", pady=20)

        if query:
            msg = f"No resumes found matching '{query}'."
        else:
            msg = "You haven't created any resumes yet."

        tk.Label(
            empty_frame,
            text=msg,
            font=(THEME["font_family"], 11, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        ).pack(pady=(0, 6))

        tk.Label(
            empty_frame,
            text="Click '+ Create New Resume' to build your first tailored resume.",
            font=(THEME["font_family"], 9),
            bg="#FFFFFF",
            fg=THEME["text_muted"],
        ).pack(pady=(0, 16))

        create_button(
            empty_frame,
            "+ Create New Resume",
            self._create_new_resume,
            style_type="primary",
        ).pack()

    def _render_resume_card(self, resume: Resume):
        card = tk.Frame(
            self.list_container,
            bg="#FFFFFF",
            bd=1,
            relief="solid",
            padx=20,
            pady=16,
        )
        card.pack(fill="x", pady=8)

        # Left Info
        info_f = tk.Frame(card, bg="#FFFFFF")
        info_f.pack(side="left", fill="x", expand=True)

        title_lbl = tk.Label(
            info_f,
            text=resume.title,
            font=(THEME["font_family"], 12, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
            cursor="hand2",
        )
        title_lbl.pack(anchor="w")
        title_lbl.bind("<Button-1>", lambda e, r=resume: self.on_open_resume(r))

        sub_info = f"Last modified: {resume.updated_at}   |   Template: {resume.template_name.capitalize()}"
        if resume.personal_info.full_name:
            sub_info = f"Name: {resume.personal_info.full_name}   |   " + sub_info

        tk.Label(
            info_f,
            text=sub_info,
            font=(THEME["font_family"], 9),
            bg="#FFFFFF",
            fg=THEME["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        # Right Actions
        btn_f = tk.Frame(card, bg="#FFFFFF")
        btn_f.pack(side="right")

        create_button(btn_f, "Edit", lambda r=resume: self.on_open_resume(r), style_type="primary").pack(side="left", padx=4)
        create_button(btn_f, "Duplicate", lambda r=resume: self._duplicate_resume(r), style_type="outline").pack(side="left", padx=4)
        create_button(btn_f, "Export PDF", lambda r=resume: self._export_resume(r), style_type="outline").pack(side="left", padx=4)
        create_button(btn_f, "Delete", lambda r=resume: self._delete_resume(r), style_type="danger").pack(side="left", padx=4)

    def _create_new_resume(self):
        dlg = PromptDialog(self, "Create New Resume", "Enter resume title (e.g. Software Engineer):", "Software Engineer Resume")
        if dlg.result:
            new_resume = self.resume_service.create_resume(title=dlg.result)
            self.on_open_resume(new_resume)

    def _build_from_jd_action(self):
        # Create draft resume and open straight into JD Tailor tool
        new_resume = self.resume_service.create_resume(title="Targeted Job Resume")
        self.on_open_resume(new_resume)

    def _duplicate_resume(self, resume: Resume):
        dlg = PromptDialog(self, "Duplicate Resume", "Enter duplicate title:", f"{resume.title} (Copy)")
        if dlg.result and resume.id:
            self.resume_service.duplicate_resume(resume.id, dlg.result)
            self.refresh(self.entry_search.get().strip())

    def _export_resume(self, resume: Resume):
        self.resume_service.export_pdf(resume, open_after=True)

    def _delete_resume(self, resume: Resume):
        dlg = ConfirmDialog(
            self,
            "Delete Resume",
            f"Are you sure you want to delete '{resume.title}'? This action cannot be undone.",
            confirm_label="Delete",
        )
        if dlg.confirmed and resume.id:
            self.resume_service.delete_resume(resume.id)
            self.refresh(self.entry_search.get().strip())

    def _on_search(self, event=None):
        query = self.entry_search.get().strip()
        self.refresh(query)
