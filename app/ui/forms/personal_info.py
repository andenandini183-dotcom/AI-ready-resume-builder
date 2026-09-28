"""
Personal Information Form View.
"""

import tkinter as tk
from typing import Callable, Optional
from app.models.personal_info import PersonalInfo
from app.config.settings import THEME


class PersonalInfoForm(tk.Frame):
    """Form view for editing Personal Information and Summary."""

    def __init__(self, parent: tk.Widget, personal_info: PersonalInfo, on_change: Callable[[], None]):
        super().__init__(parent, bg="#FFFFFF", padx=24, pady=24)
        self.personal_info = personal_info
        self.on_change = on_change
        self._is_loading = False

        self._build_ui()
        self.load_data(personal_info)

    def _build_ui(self):
        # Section Title
        lbl_title = tk.Label(
            self,
            text="Personal Information",
            font=(THEME["font_family"], 14, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        )
        lbl_title.pack(anchor="w", pady=(0, 4))

        lbl_sub = tk.Label(
            self,
            text="Enter your contact details and professional summary.",
            font=(THEME["font_family"], 9),
            bg="#FFFFFF",
            fg=THEME["text_muted"],
        )
        lbl_sub.pack(anchor="w", pady=(0, 20))

        # Form Fields Grid
        grid_frame = tk.Frame(self, bg="#FFFFFF")
        grid_frame.pack(fill="x")
        grid_frame.columnconfigure(0, weight=1, pad=12)
        grid_frame.columnconfigure(1, weight=1, pad=12)

        # 1. Full Name
        self.entries = {}
        self._add_field(grid_frame, "full_name", "Full Name *", 0, 0)
        self._add_field(grid_frame, "title", "Professional Title", 0, 1)

        self._add_field(grid_frame, "email", "Email Address *", 1, 0)
        self._add_field(grid_frame, "phone", "Phone Number", 1, 1)

        self._add_field(grid_frame, "location", "Location (City, State/Country)", 2, 0)
        self._add_field(grid_frame, "linkedin", "LinkedIn URL", 2, 1)

        self._add_field(grid_frame, "github", "GitHub URL", 3, 0)
        self._add_field(grid_frame, "portfolio", "Portfolio / Website URL", 3, 1)

        # Professional Summary Text Area
        lbl_sum = tk.Label(
            self,
            text="Professional Summary",
            font=(THEME["font_family"], 9, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        )
        lbl_sum.pack(anchor="w", pady=(16, 6))

        self.txt_summary = tk.Text(
            self,
            font=(THEME["font_family"], 9),
            bg="#F8FAFC",
            fg=THEME["text_dark"],
            bd=1,
            relief="solid",
            height=6,
            wrap="word",
        )
        self.txt_summary.pack(fill="x")
        self.txt_summary.bind("<KeyRelease>", self._on_field_change)

    def _add_field(self, parent: tk.Widget, key: str, label_text: str, row: int, col: int):
        f = tk.Frame(parent, bg="#FFFFFF")
        f.grid(row=row, column=col, sticky="ew", pady=8)

        lbl = tk.Label(
            f,
            text=label_text,
            font=(THEME["font_family"], 9, "bold"),
            bg="#FFFFFF",
            fg=THEME["text_dark"],
        )
        lbl.pack(anchor="w", pady=(0, 4))

        entry = tk.Entry(
            f,
            font=(THEME["font_family"], 9),
            bg="#F8FAFC",
            fg=THEME["text_dark"],
            bd=1,
            relief="solid",
        )
        entry.pack(fill="x", ipady=4)
        entry.bind("<KeyRelease>", self._on_field_change)
        self.entries[key] = entry

    def load_data(self, info: PersonalInfo):
        self._is_loading = True
        self.personal_info = info
        
        data_dict = info.to_dict()
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data_dict.get(key, ""))

        self.txt_summary.delete("1.0", tk.END)
        self.txt_summary.insert("1.0", info.summary or "")
        self._is_loading = False

    def save_data(self) -> PersonalInfo:
        for key, entry in self.entries.items():
            setattr(self.personal_info, key, entry.get().strip())
        self.personal_info.summary = self.txt_summary.get("1.0", tk.END).strip()
        return self.personal_info

    def _on_field_change(self, event=None):
        if not self._is_loading:
            self.save_data()
            self.on_change()
