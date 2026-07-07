"""Student Management System — Tkinter GUI with JSON file persistence."""

from __future__ import annotations
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).parent / "students.json"

BG, SURFACE, CARD = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD, BAD, GOLD = "#bb9af7", "#9ece6a", "#f7768e", "#e0af68"
TEXT, MUTED = "#c0caf5", "#565f89"
FONT = ("Segoe UI", 12)


class StudentDB:
    """Simple dict-backed CRUD store, persisted as JSON."""

    def __init__(self, path: Path):
        self._path = path
        self._data: dict[str, dict] = {}
        if path.exists():
            try:
                self._data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    def _save(self):
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False),
                               encoding="utf-8")

    def add(self, student: dict) -> str:
        sid = f"STU{datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]}"
        self._data[sid] = {**student, "id": sid}
        self._save()
        return sid

    def update(self, sid: str, fields: dict):
        if sid in self._data:
            self._data[sid].update(fields)
            self._save()

    def delete(self, sid: str):
        self._data.pop(sid, None)
        self._save()

    def get(self, sid: str) -> dict | None:
        return self._data.get(sid)

    def all(self) -> list[dict]:
        return list(self._data.values())

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [s for s in self._data.values()
                if q in s.get("name", "").lower()
                or q in s.get("id", "").lower()
                or q in s.get("course", "").lower()]


db = StudentDB(DATA_FILE)


def style_treeview():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                     foreground=TEXT, rowheight=32, font=FONT)
    style.configure("Treeview.Heading", background=CARD, foreground=ACCENT,
                     font=("Segoe UI", 12, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", BG)])


class StudentApp(tk.Tk):
    COLS = ("ID", "Name", "Age", "Course", "GPA", "Enrolled")

    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("920x620")
        self.configure(bg=BG)
        self.minsize(800, 500)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Frame(self, bg=SURFACE, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Student Management System", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 19, "bold")).pack(side="left", padx=20)
        self.count_lbl = tk.Label(header, bg=SURFACE, fg=MUTED, font=FONT)
        self.count_lbl.pack(side="right", padx=20)

        toolbar = tk.Frame(self, bg=BG, pady=10)
        toolbar.pack(fill="x", padx=16)
        tk.Entry(toolbar, textvariable=self.search_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, font=("Segoe UI", 13), relief="flat",
                 width=24).pack(side="left", padx=(0, 20), ipady=5)

        for text, cmd, color in [("Add", self.add, GOOD), ("Edit", self.edit, GOLD),
                                  ("Delete", self.delete, BAD)]:
            tk.Button(toolbar, text=text, bg=color, fg=BG, font=("Segoe UI", 11, "bold"),
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      command=cmd).pack(side="left", padx=4)

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        style_treeview()
        self.tree = ttk.Treeview(tree_frame, columns=self.COLS, show="headings",
                                  selectmode="browse")
        for col, w in zip(self.COLS, [160, 180, 60, 160, 70, 130]):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit())

        self.stats_bar = tk.Frame(self, bg=SURFACE, pady=8)
        self.stats_bar.pack(fill="x")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.search_var.get()
        rows = db.search(query) if query else db.all()

        for c in (GOOD, GOLD, BAD):
            self.tree.tag_configure(c, foreground=c)

        for s in rows:
            gpa = s.get("gpa", "")
            color = GOOD if isinstance(gpa, (int, float)) and gpa >= 3.5 else \
                    GOLD if isinstance(gpa, (int, float)) and gpa >= 2.5 else BAD
            self.tree.insert("", "end", iid=s["id"], values=(
                s["id"], s.get("name", ""), s.get("age", ""), s.get("course", ""),
                f"{gpa:.2f}" if isinstance(gpa, float) else gpa, s.get("enrolled", "")
            ), tags=(color,))

        self.count_lbl.config(text=f"{len(rows)} student(s)")
        self._update_stats(rows)

    def _update_stats(self, rows: list[dict]):
        for w in self.stats_bar.winfo_children():
            w.destroy()
        if not rows:
            return

        gpas = [s["gpa"] for s in rows if isinstance(s.get("gpa"), (int, float))]
        avg = sum(gpas) / len(gpas) if gpas else 0
        courses: dict[str, int] = {}
        for s in rows:
            courses[s.get("course", "?")] = courses.get(s.get("course", "?"), 0) + 1
        top = max(courses, key=courses.get) if courses else "—"

        for text in (f"  Avg GPA: {avg:.2f}", f"  Top Course: {top}", f"  Total: {len(rows)}"):
            tk.Label(self.stats_bar, text=text, bg=SURFACE, fg=MUTED,
                     font=("Segoe UI", 11)).pack(side="left", padx=16)

    def _sort(self, col: str):
        rows = sorted((self.tree.set(k, col), k) for k in self.tree.get_children(""))
        for idx, (_, k) in enumerate(rows):
            self.tree.move(k, "", idx)

    def _selected_id(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def add(self):
        dialog = StudentDialog(self, "Add Student")
        self.wait_window(dialog)
        if dialog.result:
            db.add(dialog.result)
            self.refresh()

    def edit(self):
        sid = self._selected_id()
        if not sid:
            messagebox.showinfo("Select", "Please select a student first.")
            return
        dialog = StudentDialog(self, "Edit Student", db.get(sid))
        self.wait_window(dialog)
        if dialog.result:
            db.update(sid, dialog.result)
            self.refresh()

    def delete(self):
        sid = self._selected_id()
        if not sid:
            messagebox.showinfo("Select", "Please select a student first.")
            return
        student = db.get(sid)
        if messagebox.askyesno("Delete", f"Delete student '{student['name']}'?"):
            db.delete(sid)
            self.refresh()


class StudentDialog(tk.Toplevel):
    FIELDS = [("Name", "name", str), ("Age", "age", int),
              ("Course", "course", str), ("GPA", "gpa", float)]

    def __init__(self, parent, title: str, data: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        tk.Label(self, text=title, bg=BG, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(pady=(16, 12))

        form = tk.Frame(self, bg=BG)
        form.pack(padx=30, fill="x")

        self.vars: dict[str, tk.StringVar] = {}
        for row, (label, key, _) in enumerate(self.FIELDS):
            tk.Label(form, text=label, bg=BG, fg=TEXT, font=FONT, width=10, anchor="w"
                     ).grid(row=row, column=0, pady=6, sticky="w")
            var = tk.StringVar(value=str(data.get(key, "")) if data else "")
            self.vars[key] = var
            tk.Entry(form, textvariable=var, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                     font=FONT, relief="flat", width=26).grid(
                row=row, column=1, pady=6, padx=(10, 0), ipady=5)

        self.enrolled = data.get("enrolled") if data else None
        self.enrolled = self.enrolled or datetime.now().strftime("%Y-%m-%d")

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=16)
        tk.Button(btn_row, text="Save", bg=ACCENT, fg=BG, font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=self._save).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel", bg=SURFACE, fg=TEXT, font=FONT, relief="flat",
                  padx=16, pady=6, cursor="hand2", command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        result = {}
        for label, key, cast in self.FIELDS:
            raw = self.vars[key].get().strip()
            if not raw:
                messagebox.showerror("Validation", f"{label} cannot be empty.", parent=self)
                return
            try:
                result[key] = cast(raw)
            except ValueError:
                messagebox.showerror("Validation", f"Invalid value for {label}.", parent=self)
                return

        if not (0 <= result["gpa"] <= 4.0):
            messagebox.showerror("Validation", "GPA must be 0.0–4.0.", parent=self)
            return

        result["enrolled"] = self.enrolled
        self.result = result
        self.destroy()


if __name__ == "__main__":
    StudentApp().mainloop()
