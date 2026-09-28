"""
Skills Form View.
"""

import tkinter as tk
from typing import List, Callable, Optional
from app.models.skill import Skill
from app.config.settings import THEME
from app.ui.components.buttons import create_button


class SkillsForm(tk.Frame):
    """Form for managing multiple Skill records."""

    def __init__(self, parent: tk.Widget, skills_list: List[Skill], on_change: Callable[[], None]):
        super().__init__(parent, bg="#FFFFFF", padx=24, pady=24)
        self.skills_list = skills_list
        self.on_change = on_change
        self.editing_index: Optional[int] = None

        self._build_ui()
        self.render_list()

    def _build_ui(self):
        hdr = tk.Frame(self, bg="#FFFFFF")
        hdr.pack(fill="x", pady=(0, 16))

        title_frame = tk.Frame(hdr, bg="#FFFFFF")
        title_frame.pack(side="left")

        tk.Label(title_frame, text="Skills & Competencies", font=(THEME["font_family"], 14, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(title_frame, text="Group skills by category and proficiency level.", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

        btn_add = create_button(hdr, "+ Add Skill", self._open_add_dialog, style_type="primary")
        btn_add.pack(side="right")

        self.cards_container = tk.Frame(self, bg="#FFFFFF")
        self.cards_container.pack(fill="both", expand=True)

    def render_list(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        if not self.skills_list:
            empty = tk.Label(
                self.cards_container,
                text="No skills added yet. Click '+ Add Skill' to get started.",
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

        for idx, sk in enumerate(self.skills_list):
            card = tk.Frame(self.cards_container, bg="#FFFFFF", bd=1, relief="solid", padx=16, pady=10)
            card.pack(fill="x", pady=4)

            info_f = tk.Frame(card, bg="#FFFFFF")
            info_f.pack(side="left", fill="x", expand=True)

            prof = f" ({sk.proficiency})" if sk.proficiency else ""
            tk.Label(info_f, text=f"{sk.skill_name}{prof}", font=(THEME["font_family"], 10, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
            tk.Label(info_f, text=sk.category or "Technical Skills", font=(THEME["font_family"], 8), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

            btn_f = tk.Frame(card, bg="#FFFFFF")
            btn_f.pack(side="right")

            create_button(btn_f, "Edit", lambda i=idx: self._open_edit_dialog(i), style_type="outline").pack(side="left", padx=4)
            create_button(btn_f, "Delete", lambda i=idx: self._delete_item(i), style_type="danger").pack(side="left")

    def _open_add_dialog(self):
        SkillItemDialog(self, Skill(), self._save_item)

    def _open_edit_dialog(self, index: int):
        self.editing_index = index
        SkillItemDialog(self, self.skills_list[index], self._save_item)

    def _save_item(self, item: Skill):
        if self.editing_index is not None:
            self.skills_list[self.editing_index] = item
            self.editing_index = None
        else:
            self.skills_list.append(item)
        self.render_list()
        self.on_change()

    def _delete_item(self, index: int):
        del self.skills_list[index]
        self.render_list()
        self.on_change()


class SkillItemDialog(tk.Toplevel):
    """Modal dialog to add or edit a Skill record."""

    def __init__(self, parent: tk.Widget, item: Skill, on_save: Callable[[Skill], None]):
        super().__init__(parent)
        self.title("Skill Entry")
        self.item = item
        self.on_save = on_save
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(bg="#FFFFFF")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        f = tk.Frame(self, bg="#FFFFFF", padx=20, pady=16)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Skill Name *", font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(4, 1))
        self.entry_name = tk.Entry(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid")
        self.entry_name.insert(0, self.item.skill_name)
        self.entry_name.pack(fill="x", ipady=3)

        tk.Label(f, text="Category", font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(8, 1))
        self.entry_cat = tk.Entry(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid")
        self.entry_cat.insert(0, self.item.category or "Technical Skills")
        self.entry_cat.pack(fill="x", ipady=3)

        tk.Label(f, text="Proficiency Level (Optional)", font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w", pady=(8, 1))
        self.entry_prof = tk.Entry(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid")
        self.entry_prof.insert(0, self.item.proficiency or "")
        self.entry_prof.pack(fill="x", ipady=3)

        btn_f = tk.Frame(f, bg="#FFFFFF")
        btn_f.pack(anchor="e", pady=20)
        create_button(btn_f, "Cancel", self.destroy, style_type="outline").pack(side="left", padx=6)
        create_button(btn_f, "Save Skill", self._submit, style_type="primary").pack(side="left")

    def _submit(self):
        self.item.skill_name = self.entry_name.get().strip()
        self.item.category = self.entry_cat.get().strip() or "Technical Skills"
        self.item.proficiency = self.entry_prof.get().strip()
        if self.item.skill_name:
            self.on_save(self.item)
        self.destroy()
