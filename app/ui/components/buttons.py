"""
Reusable Custom Styled Button Components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from app.config.settings import THEME


def create_button(
    parent: tk.Widget,
    text: str,
    command: Callable[[], None],
    style_type: str = "primary",
    width: Optional[int] = None,
) -> tk.Button:
    """Creates a modern flat styled Tkinter button."""

    if style_type == "primary":
        bg = THEME["accent"]
        fg = "#FFFFFF"
        active_bg = THEME["accent_hover"]
    elif style_type == "secondary":
        bg = THEME["primary"]
        fg = "#FFFFFF"
        active_bg = THEME["primary_hover"]
    elif style_type == "danger":
        bg = THEME["danger"]
        fg = "#FFFFFF"
        active_bg = THEME["danger_hover"]
    elif style_type == "outline":
        bg = "#FFFFFF"
        fg = THEME["text_dark"]
        active_bg = "#F1F5F9"
    else:
        bg = "#E2E8F0"
        fg = THEME["text_dark"]
        active_bg = "#CBD5E1"

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=active_bg,
        activeforeground=fg,
        font=(THEME["font_family"], 9, "bold" if style_type in ["primary", "danger"] else "normal"),
        relief="flat",
        bd=0,
        padx=14,
        pady=7,
        cursor="hand2",
    )

    if width:
        btn.config(width=width)

    return btn
