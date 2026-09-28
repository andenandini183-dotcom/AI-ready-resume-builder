"""
Experience Form View.
"""

import tkinter as tk
from typing import List, Callable, Optional
from app.models.experience import Experience
from app.config.settings import THEME
from app.ui.components.buttons import create_button


class ExperienceForm(tk.Frame):
    """Form for managing multiple Work Experience records."""

    def __init__(self, parent: tk.Widget, experience_list: List[Experience], on_change: Callable[[], None]):
        super().__init__(parent, bg="#FFFFFF", padx=24, pady=24)
        self.experience_list = experience_list
        self.on_change = on_change
        self.editing_index: Optional[int] = None

        self._build_ui()
        self.render_list()

    def _build_ui(self):
        hdr = tk.Frame(self, bg="#FFFFFF")
        hdr.pack(fill="x", pady=(0, 16))

        title_frame = tk.Frame(hdr, bg="#FFFFFF")
        title_frame.pack(side="left")

        tk.Label(title_frame, text="Work Experience", font=(THEME["font_family"], 14, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(title_frame, text="Add your professional roles, responsibilities, and achievements.", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

        btn_add = create_button(hdr, "+ Add Experience", self._open_add_dialog, style_type="primary")
        btn_add.pack(side="right")

        self.cards_container = tk.Frame(self, bg="#FFFFFF")
        self.cards_container.pack(fill="both", expand=True)

    def render_list(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        if not self.experience_list:
            empty = tk.Label(
                self.cards_container,
                text="No work experience added yet. Click '+ Add Experience' to get started.",
                font=(THEME["font_family"], 9, "italic"),
                bg="#F8FAFC",
                fg=THEME["text_muted"],
                padx=20,
                pady=30,
                bd=1,
                relief="solid",
            )
            empty.pack(fill="x", pady=10)
            return

        for idx, exp in enumerate(self.experience_list):
            card = tk.Frame(self.cards_container, bg="#FFFFFF", bd=1, relief="solid", padx=16, pady=12)
            card.pack(fill="x", pady=6)

            info_f = tk.Frame(card, bg="#FFFFFF")
            info_f.pack(side="left", fill="x", expand=True)

            pos_text = f"{exp.position} — {exp.company}" if exp.position and exp.company else (exp.position or exp.company)
            tk.Label(info_f, text=pos_text, font=(THEME["font_family"], 10, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
            
            dates = f"{exp.start_date} – {'Present' if exp.is_current else exp.end_date}"
            sub = f"{dates} | {exp.location}".strip(" | ")
            tk.Label(info_f, text=sub, font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

            btn_f = tk.Frame(card, bg="#FFFFFF")
            btn_f.pack(side="right")

            create_button(btn_f, "Edit", lambda i=idx: self._open_edit_dialog(i), style_type="outline").pack(side="left", padx=4)
            create_button(btn_f, "Delete", lambda i=idx: self._delete_item(i), style_type="danger").pack(side="left")

    def _open_add_dialog(self):
        ExperienceItemDialog(self, Experience(), self._save_item)

    def _open_edit_dialog(self, index: int):
        self.editing_index = index
        ExperienceItemDialog(self, self.experience_list[index], self._save_item)

    def _save_item(self, item: Experience):
        if self.editing_index is not None:
            self.experience_list[self.editing_index] = item
            self.editing_index = None
        else:
            self.experience_list.append(item)
        self.render_list()
        self.on_change()

    def _delete_item(self, index: int):
        del self.experience_list[index]
        self.render_list()
        self.on_change()


class ExperienceItemDialog(tk.Toplevel):
    """Modal dialog to add or edit a Work Experience record."""

    def __init__(self, parent: tk.Widget, item: Experience, on_save: Callable[[Experience], None]):
        super().__init__(parent)
        self.title("Work Experience Entry")
        self.item = item
        self.on_save = on_save
        self.geometry("520x560")
        self.resizable(False, False)
        self.configure(bg="#FFFFFF")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        f = tk.Frame(self, bg="#FFFFFF", padx=20, pady=16)
        f.pack(fill="both", expand=True)

        self.entries = {}
        fields = [
            ("company", "Company / Organization *"),
            ("position", "Position / Job Title *"),
            ("location", "Location (City, State)"),
            ("start_date", "Start Date (YYYY-MM)"),
            ("end_date", "End Date (YYYY-MM or Present)"),
        ]

        for key, label in fields:
            lbl = tk.Label(f, text=label, font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"])
            lbl.pack(anchor="w", pady=(4, 1))
            entry = tk.Entry(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid")
            entry.insert(0, getattr(self.item, key, ""))
            entry.pack(fill="x", ipady=3)
            self.entries[key] = entry

        # Current Job Checkbox
        self.var_current = tk.BooleanVar(value=self.item.is_current)
        chk = tk.Checkbutton(
            f, text="I currently work here", variable=self.var_current, bg="#FFFFFF", font=(THEME["font_family"], 9)
        )
        chk.pack(anchor="w", pady=6)

        # Responsibilities
        tk.Label(f, text="Responsibilities (one bullet per line)", font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(4, 1))
        self.txt_resp = tk.Text(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid", height=4, wrap="word")
        self.txt_resp.insert("1.0", self.item.responsibilities or "")
        self.txt_resp.pack(fill="x")

        # Key Achievements
        tk.Label(f, text="Key Achievements (optional, one bullet per line)", font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(4, 1))
        self.txt_ach = tk.Text(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid", height=3, wrap="word")
        self.txt_ach.insert("1.0", self.item.achievements or "")
        self.txt_ach.pack(fill="x")

        btn_f = tk.Frame(f, bg="#FFFFFF")
        btn_f.pack(anchor="e", pady=16)
        create_button(btn_f, "Cancel", self.destroy, style_type="outline").pack(side="left", padx=6)
        create_button(btn_f, "Save Entry", self._submit, style_type="primary").pack(side="left")

    def _submit(self):
        for key, entry in self.entries.items():
            setattr(self.item, key, entry.get().strip())
        self.item.is_current = self.var_current.get()
        self.item.responsibilities = self.txt_resp.get("1.0", tk.END).strip()
        self.item.achievements = self.txt_ach.get("1.0", tk.END).strip()
        self.on_save(self.item)
        self.destroy()
