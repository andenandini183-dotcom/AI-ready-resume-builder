"""
Top Header Navigation Bar Component for Resume Editor.
"""

import tkinter as tk
from typing import Callable
from app.config.settings import THEME
from app.ui.components.buttons import create_button


class Navbar(tk.Frame):
    """Top navigation bar for Resume Editor header actions."""

    def __init__(
        self,
        parent: tk.Widget,
        resume_title: str,
        on_back: Callable[[], None],
        on_title_click: Callable[[], None],
        on_export: Callable[[], None],
        on_save: Callable[[], None],
    ):
        super().__init__(parent, bg="#FFFFFF", height=56, highlightthickness=1, highlightbackground=THEME["card_border"])
        self.on_back = on_back
        self.on_title_click = on_title_click
        self.on_export = on_export
        self.on_save = on_save

        self.pack_propagate(False)
        self._build_ui(resume_title)

    def _build_ui(self, title: str):
        # Left Side: Back button and Resume Title
        left_frame = tk.Frame(self, bg="#FFFFFF")
        left_frame.pack(side="left", padx=16, pady=8)

        btn_back = tk.Button(
            left_frame,
            text="← Dashboard",
            command=self.on_back,
            bg="#F1F5F9",
            fg=THEME["text_dark"],
            font=(THEME["font_family"], 9, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
        )
        btn_back.pack(side="left", padx=(0, 16))

        self.lbl_title = tk.Button(
            left_frame,
            text=f"{title}  ✏️",
            command=self.on_title_click,
            bg="#FFFFFF",
            fg=THEME["text_dark"],
            font=(THEME["font_family"], 12, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self.lbl_title.pack(side="left")

        # Right Side: Status indicator and Actions
        right_frame = tk.Frame(self, bg="#FFFFFF")
        right_frame.pack(side="right", padx=16, pady=8)

        self.lbl_status = tk.Label(
            right_frame,
            text="Saved",
            font=(THEME["font_family"], 8, "bold"),
            bg="#ECFDF5",
            fg=THEME["success"],
            padx=10,
            pady=4,
        )
        self.lbl_status.pack(side="left", padx=(0, 12))

        btn_save = create_button(right_frame, "Save", self.on_save, style_type="outline")
        btn_save.pack(side="left", padx=(0, 8))

        btn_export = create_button(right_frame, "Export PDF", self.on_export, style_type="primary")
        btn_export.pack(side="left")

    def update_title(self, title: str):
        self.lbl_title.config(text=f"{title}  ✏️")

    def set_status(self, status: str):
        if status == "Saving...":
            self.lbl_status.config(text="Saving...", bg="#FEF3C7", fg=THEME["warning"])
        elif status == "Saved":
            self.lbl_status.config(text="Saved", bg="#ECFDF5", fg=THEME["success"])
        elif status == "Unsaved changes":
            self.lbl_status.config(text="Unsaved changes", bg="#FEF2F2", fg=THEME["danger"])
