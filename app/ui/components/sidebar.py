"""
Left Navigation Sidebar Component for Resume Editor.
"""

import tkinter as tk
from typing import Callable, Dict
from app.config.settings import THEME


class Sidebar(tk.Frame):
    """Left sidebar widget for switching editor sections and tools."""

    SECTIONS = [
        ("personal_info", "Personal Information"),
        ("education", "Education"),
        ("experience", "Experience"),
        ("projects", "Projects"),
        ("skills", "Skills"),
        ("certifications", "Certifications"),
    ]

    TOOLS = [
        ("preview", "Live Preview"),
        ("templates", "Template Selection"),
        ("ats_analysis", "ATS Analysis"),
        ("jd_tailor", "JD Match & Tailor"),
        ("export", "Export PDF"),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        on_section_change: Callable[[str], None],
        active_section: str = "personal_info",
    ):
        super().__init__(parent, bg=THEME["bg_dark"], width=220)
        self.on_section_change = on_section_change
        self.active_section = active_section
        self.buttons: Dict[str, tk.Button] = {}

        self.pack_propagate(False)
        self._build_ui()

    def _build_ui(self):
        # Section Group: RESUME SECTIONS
        lbl_sec = tk.Label(
            self,
            text="RESUME SECTIONS",
            font=(THEME["font_family"], 8, "bold"),
            bg=THEME["bg_dark"],
            fg=THEME["text_muted"],
            anchor="w",
            padx=16,
            pady=12,
        )
        lbl_sec.pack(fill="x")

        for key, label in self.SECTIONS:
            btn = self._create_nav_button(key, label)
            btn.pack(fill="x", padx=8, pady=2)
            self.buttons[key] = btn

        # Section Group: TOOLS
        lbl_tools = tk.Label(
            self,
            text="TOOLS & EXPORT",
            font=(THEME["font_family"], 8, "bold"),
            bg=THEME["bg_dark"],
            fg=THEME["text_muted"],
            anchor="w",
            padx=16,
            pady=16,
        )
        lbl_tools.pack(fill="x")

        for key, label in self.TOOLS:
            btn = self._create_nav_button(key, label)
            btn.pack(fill="x", padx=8, pady=2)
            self.buttons[key] = btn

        self.set_active(self.active_section)

    def _create_nav_button(self, key: str, label: str) -> tk.Button:
        btn = tk.Button(
            self,
            text=f"   {label}",
            anchor="w",
            font=(THEME["font_family"], 9, "bold" if key == self.active_section else "normal"),
            bg=THEME["bg_dark"],
            fg=THEME["text_light"],
            activebackground=THEME["primary"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=lambda k=key: self._on_btn_click(k),
        )
        return btn

    def _on_btn_click(self, key: str):
        self.set_active(key)
        self.on_section_change(key)

    def set_active(self, key: str):
        self.active_section = key
        for k, btn in self.buttons.items():
            if k == key:
                btn.config(
                    bg=THEME["accent"],
                    fg="#FFFFFF",
                    font=(THEME["font_family"], 9, "bold"),
                )
            else:
                btn.config(
                    bg=THEME["bg_dark"],
                    fg=THEME["text_light"],
                    font=(THEME["font_family"], 9, "normal"),
                )
