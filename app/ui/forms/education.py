"""
Education Form View.
"""

import tkinter as tk
from typing import List, Callable, Optional
from app.models.education import Education
from app.config.settings import THEME
from app.ui.components.buttons import create_button


class EducationForm(tk.Frame):
    """Form for managing multiple Education records."""

    def __init__(self, parent: tk.Widget, education_list: List[Education], on_change: Callable[[], None]):
        super().__init__(parent, bg="#FFFFFF", padx=24, pady=24)
        self.education_list = education_list
        self.on_change = on_change
        self.editing_index: Optional[int] = None

        self._build_ui()
        self.render_list()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#FFFFFF")
        hdr.pack(fill="x", pady=(0, 16))

        title_frame = tk.Frame(hdr, bg="#FFFFFF")
        title_frame.pack(side="left")

        tk.Label(title_frame, text="Education History", font=(THEME["font_family"], 14, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
        tk.Label(title_frame, text="Add your academic degrees, institutions, and honors.", font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

        btn_add = create_button(hdr, "+ Add Education", self._open_add_dialog, style_type="primary")
        btn_add.pack(side="right")

        # Container for card list
        self.cards_container = tk.Frame(self, bg="#FFFFFF")
        self.cards_container.pack(fill="both", expand=True)

    def render_list(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        if not self.education_list:
            empty = tk.Label(
                self.cards_container,
                text="No education entries added yet. Click '+ Add Education' to get started.",
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

        for idx, edu in enumerate(self.education_list):
            card = tk.Frame(self.cards_container, bg="#FFFFFF", bd=1, relief="solid", padx=16, pady=12)
            card.pack(fill="x", pady=6)

            info_f = tk.Frame(card, bg="#FFFFFF")
            info_f.pack(side="left", fill="x", expand=True)

            degree_text = f"{edu.degree} in {edu.field_of_study}".strip(" in ") if edu.degree or edu.field_of_study else "Degree / Field"
            tk.Label(info_f, text=degree_text, font=(THEME["font_family"], 10, "bold"), bg="#FFFFFF", fg=THEME["text_dark"]).pack(anchor="w")
            
            sub = f"{edu.institution} | {edu.start_date} – {edu.end_date}".strip(" | ")
            if edu.gpa:
                sub += f" (GPA: {edu.gpa})"
            tk.Label(info_f, text=sub, font=(THEME["font_family"], 9), bg="#FFFFFF", fg=THEME["text_muted"]).pack(anchor="w")

            btn_f = tk.Frame(card, bg="#FFFFFF")
            btn_f.pack(side="right")

            create_button(btn_f, "Edit", lambda i=idx: self._open_edit_dialog(i), style_type="outline").pack(side="left", padx=4)
            create_button(btn_f, "Delete", lambda i=idx: self._delete_item(i), style_type="danger").pack(side="left")

    def _open_add_dialog(self):
        EducationItemDialog(self, Education(), self._save_item)

    def _open_edit_dialog(self, index: int):
        self.editing_index = index
        EducationItemDialog(self, self.education_list[index], self._save_item)

    def _save_item(self, item: Education):
        if self.editing_index is not None:
            self.education_list[self.editing_index] = item
            self.editing_index = None
        else:
            self.education_list.append(item)
        self.render_list()
        self.on_change()

    def _delete_item(self, index: int):
        del self.education_list[index]
        self.render_list()
        self.on_change()


class EducationItemDialog(tk.Toplevel):
    """Modal dialog to add or edit an Education record."""

    def __init__(self, parent: tk.Widget, item: Education, on_save: Callable[[Education], None]):
        super().__init__(parent)
        self.title("Education Entry")
        self.item = item
        self.on_save = on_save
        self.geometry("450x440")
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
            ("institution", "Institution / University *"),
            ("degree", "Degree (e.g. Bachelor of Science)"),
            ("field_of_study", "Field of Study / Major"),
            ("start_date", "Start Date (YYYY-MM)"),
            ("end_date", "End Date (YYYY-MM or Present)"),
            ("gpa", "GPA / Grade"),
            ("description", "Honors / Description"),
        ]

        for key, label in fields:
            lbl = tk.Label(f, text=label, font=(THEME["font_family"], 9, "bold"), bg="#FFFFFF", fg=THEME["text_dark"])
            lbl.pack(anchor="w", pady=(6, 2))
            entry = tk.Entry(f, font=(THEME["font_family"], 9), bg="#F8FAFC", bd=1, relief="solid")
            entry.insert(0, getattr(self.item, key, ""))
            entry.pack(fill="x", ipady=3)
            self.entries[key] = entry

        btn_f = tk.Frame(f, bg="#FFFFFF")
        btn_f.pack(anchor="e", pady=20)
        create_button(btn_f, "Cancel", self.destroy, style_type="outline").pack(side="left", padx=6)
        create_button(btn_f, "Save Entry", self._submit, style_type="primary").pack(side="left")

    def _submit(self):
        for key, entry in self.entries.items():
            setattr(self.item, key, entry.get().strip())
        self.on_save(self.item)
        self.destroy()
