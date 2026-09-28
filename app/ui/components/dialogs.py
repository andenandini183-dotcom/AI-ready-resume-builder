"""
Custom Dialog Modals.
Provides popups for Title Edit, Confirmations, Template Selection, and ATS Report display.
"""

import tkinter as tk
from typing import Optional, Callable
from app.config.settings import THEME
from app.services.ats_analyzer import ATSResult
from app.ui.components.buttons import create_button


class PromptDialog(tk.Toplevel):
    """Custom input text prompt modal."""

    def __init__(self, parent: tk.Widget, title: str, prompt: str, initial_value: str = ""):
        super().__init__(parent)
        self.title(title)
        self.result: Optional[str] = None
        self.geometry("400x180")
        self.resizable(False, False)
        self.configure(bg="#FFFFFF")
        self.transient(parent)
        self.grab_set()

        # UI
        tk.Label(self, text=prompt, font=(THEME["font_family"], 10, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(20, 8))
        self.entry = tk.Entry(self, font=(THEME["font_family"], 10), bg="#F8FAFC", bd=1, relief="solid")
        self.entry.insert(0, initial_value)
        self.entry.pack(fill="x", padx=20, pady=(0, 20))
        self.entry.focus_set()

        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(anchor="e", padx=20)
        
        create_button(btn_frame, "Cancel", self._cancel, style_type="outline").pack(side="left", padx=(0, 8))
        create_button(btn_frame, "Save", self._ok, style_type="primary").pack(side="left")

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())
        self.wait_window()

    def _ok(self):
        val = self.entry.get().strip()
        if val:
            self.result = val
        self.destroy()

    def _cancel(self):
        self.destroy()


class ConfirmDialog(tk.Toplevel):
    """Custom confirmation modal for destructive actions."""

    def __init__(self, parent: tk.Widget, title: str, message: str, confirm_label: str = "Delete"):
        super().__init__(parent)
        self.title(title)
        self.confirmed = False
        self.geometry("420x170")
        self.resizable(False, False)
        self.configure(bg="#FFFFFF")
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text=title, font=(THEME["font_family"], 11, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(16, 6))
        tk.Label(self, text=message, font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"], wraplength=380, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(anchor="e", padx=20, pady=(0, 16))

        create_button(btn_frame, "Cancel", self._cancel, style_type="outline").pack(side="left", padx=(0, 8))
        create_button(btn_frame, confirm_label, self._confirm, style_type="danger").pack(side="left")

        self.wait_window()

    def _confirm(self):
        self.confirmed = True
        self.destroy()

    def _cancel(self):
        self.confirmed = False
        self.destroy()


class ATSReportDialog(tk.Toplevel):
    """Displays comprehensive ATS analysis results."""

    def __init__(self, parent: tk.Widget, ats_result: ATSResult):
        super().__init__(parent)
        self.title("ATS Optimization & Analysis Report")
        self.geometry("640x540")
        self.configure(bg="#FFFFFF")
        self.transient(parent)
        self.grab_set()

        self._build_ui(ats_result)

    def _build_ui(self, res: ATSResult):
        # Header Score Box
        hdr_frame = tk.Frame(self, bg=THEME["bg_dark"], pady=20)
        hdr_frame.pack(fill="x")

        score_color = THEME["success"] if res.score >= 75 else (THEME["warning"] if res.score >= 50 else THEME["danger"])
        tk.Label(hdr_frame, text=f"{res.score}/100", font=(THEME["font_family"], 28, "bold"), bg=THEME["bg_dark"], fg=score_color).pack()
        tk.Label(hdr_frame, text="ATS RESUME MATCH SCORE", font=(THEME["font_family"], 9, "bold"), bg=THEME["bg_dark"], fg="#94A3B8").pack(pady=(4, 0))

        # Scrollable Report Content
        canvas = tk.Canvas(self, bg="#FFFFFF", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#FFFFFF", padx=24, pady=16)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Critical Issues
        if res.critical_issues:
            tk.Label(scroll_frame, text="🚨 Critical Issues", font=(THEME["font_family"], 11, "bold"), bg="#FFFFFF", fg=THEME["danger"]).pack(anchor="w", pady=(10, 6))
            for issue in res.critical_issues:
                tk.Label(scroll_frame, text=f"• {issue}", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", padx=12, pady=2)

        # 2. Warnings
        if res.warnings:
            tk.Label(scroll_frame, text="⚠️ Warnings & Risks", font=(THEME["font_family"], 11, "bold"), bg="#FFFFFF", fg=THEME["warning"]).pack(anchor="w", pady=(14, 6))
            for warn in res.warnings:
                tk.Label(scroll_frame, text=f"• {warn}", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", padx=12, pady=2)

        # 3. Suggestions
        if res.suggestions:
            tk.Label(scroll_frame, text="💡 Optimization Suggestions", font=(THEME["font_family"], 11, "bold"), bg="#FFFFFF", fg=THEME["accent"]).pack(anchor="w", pady=(14, 6))
            for sug in res.suggestions:
                tk.Label(scroll_frame, text=f"• {sug}", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", padx=12, pady=2)

        # 4. Detected Keywords
        tk.Label(scroll_frame, text="✅ Detected Keywords", font=(THEME["font_family"], 11, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(14, 6))
        kw_str = ", ".join(res.detected_keywords) if res.detected_keywords else "None detected yet."
        tk.Label(scroll_frame, text=kw_str, font=(THEME["font_family"], 9), bg="#F8FAFC", fg=THEME["text_muted"], wraplength=550, justify="left", padx=8, pady=8).pack(anchor="w", fill="x")

        # 5. Recommended Keywords
        if res.missing_keywords:
            tk.Label(scroll_frame, text="🔍 High-Impact Keywords to Consider", font=(THEME["font_family"], 11, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(14, 6))
            missing_str = ", ".join(res.missing_keywords)
            tk.Label(scroll_frame, text=missing_str, font=(THEME["font_family"], 9), bg="#F8FAFC", fg=THEME["text_muted"], wraplength=550, justify="left", padx=8, pady=8).pack(anchor="w", fill="x")

        create_button(scroll_frame, "Close Report", self.destroy, style_type="primary").pack(anchor="e", pady=20)
