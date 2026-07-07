"""To-Do List — Tkinter GUI with JSON file persistence."""

import json
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).parent / "todos.json"

BG, SIDEBAR, CARD = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD, BAD, GOLD = "#7aa2f7", "#9ece6a", "#f7768e", "#e0af68"
TEXT, MUTED = "#c0caf5", "#565f89"
FONT = ("Segoe UI", 12)

PRIORITY_COLOR = {"High": BAD, "Medium": GOLD, "Low": GOOD}


def load_todos() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_todos(todos: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(todos, indent=2, ensure_ascii=False), encoding="utf-8")


def new_todo(title: str, priority: str = "Medium") -> dict:
    return {
        "id": id(object()),
        "title": title.strip(),
        "done": False,
        "priority": priority,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def button(parent, text, bg, fg, command, **kw):
    return tk.Button(parent, text=text, bg=bg, fg=fg, font=FONT, relief="flat",
                      cursor="hand2", padx=kw.pop("padx", 10), pady=kw.pop("pady", 5),
                      command=command, **kw)


class ToDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("720x580")
        self.configure(bg=BG)
        self.minsize(620, 480)

        self.todos = load_todos()
        self.filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        self.filter_var.trace_add("write", lambda *_: self.refresh())

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Frame(self, bg=SIDEBAR, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="My To-Do List", bg=SIDEBAR, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=20)
        self.stats_lbl = tk.Label(header, bg=SIDEBAR, fg=MUTED, font=FONT)
        self.stats_lbl.pack(side="right", padx=20)

        toolbar = tk.Frame(self, bg=BG, pady=8)
        toolbar.pack(fill="x", padx=16)
        tk.Entry(toolbar, textvariable=self.search_var, bg=CARD, fg=TEXT,
                 insertbackground=TEXT, font=("Segoe UI", 13), relief="flat",
                 width=22).pack(side="left", padx=(0, 16), ipady=5)

        for label in ("All", "Active", "Done"):
            tk.Radiobutton(toolbar, text=label, variable=self.filter_var, value=label,
                           bg=BG, fg=TEXT, selectcolor=CARD, activebackground=BG,
                           font=FONT, indicatoron=False, relief="flat",
                           padx=10, pady=4, cursor="hand2").pack(side="left", padx=2)

        button(toolbar, "+ Add Task", ACCENT, "white", self.add_task).pack(side="right")

        list_frame = tk.Frame(self, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG)

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner.bind("<Configure>",
                         lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<MouseWheel>",
                          lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        footer = tk.Frame(self, bg=SIDEBAR, pady=6)
        footer.pack(fill="x")
        button(footer, "Clear Done", BAD, "white", self.clear_done).pack(side="right", padx=12)

    def refresh(self):
        for widget in self.inner.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        filt = self.filter_var.get()
        shown = [
            t for t in self.todos
            if (filt == "All" or t["done"] == (filt == "Done"))
            and query in t["title"].lower()
        ]

        for todo in shown:
            self._draw_card(todo)
        if not shown:
            tk.Label(self.inner, text="Nothing here yet", bg=BG, fg=MUTED,
                     font=("Segoe UI", 14)).pack(pady=40)

        done = sum(t["done"] for t in self.todos)
        self.stats_lbl.config(text=f"{done}/{len(self.todos)} done")

    def _draw_card(self, todo: dict):
        card = tk.Frame(self.inner, bg=CARD, pady=10, padx=14)
        card.pack(fill="x", pady=4)

        done_var = tk.BooleanVar(value=todo["done"])
        tk.Checkbutton(card, variable=done_var, bg=CARD, activebackground=CARD,
                       cursor="hand2",
                       command=lambda: self._toggle(todo, done_var)).pack(side="left")

        style = ("Segoe UI", 13, "overstrike") if todo["done"] else ("Segoe UI", 13)
        tk.Label(card, text=todo["title"], bg=CARD, fg=MUTED if todo["done"] else TEXT,
                 font=style, anchor="w").pack(side="left", padx=(4, 12))

        tk.Label(card, text=todo["priority"], bg=PRIORITY_COLOR[todo["priority"]],
                 fg="white", font=("Segoe UI", 10, "bold"), padx=6, pady=1).pack(side="left")
        tk.Label(card, text=todo["created"], bg=CARD, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left", padx=8)

        tk.Button(card, text="Edit", bg=CARD, fg=ACCENT, relief="flat",
                  font=("Segoe UI", 11), cursor="hand2",
                  command=lambda: self.edit_task(todo)).pack(side="right", padx=2)
        tk.Button(card, text="Delete", bg=CARD, fg=BAD, relief="flat",
                  font=("Segoe UI", 11), cursor="hand2",
                  command=lambda: self.delete_task(todo)).pack(side="right", padx=2)

    def add_task(self):
        dialog = TaskDialog(self, "Add Task")
        self.wait_window(dialog)
        if dialog.result:
            self.todos.append(new_todo(dialog.result["title"], dialog.result["priority"]))
            save_todos(self.todos)
            self.refresh()

    def edit_task(self, todo: dict):
        dialog = TaskDialog(self, "Edit Task", todo["title"], todo["priority"])
        self.wait_window(dialog)
        if dialog.result:
            todo.update(title=dialog.result["title"], priority=dialog.result["priority"])
            save_todos(self.todos)
            self.refresh()

    def delete_task(self, todo: dict):
        if messagebox.askyesno("Delete", f"Delete '{todo['title']}'?"):
            self.todos = [t for t in self.todos if t["id"] != todo["id"]]
            save_todos(self.todos)
            self.refresh()

    def _toggle(self, todo: dict, var: tk.BooleanVar):
        todo["done"] = var.get()
        save_todos(self.todos)
        self.refresh()

    def clear_done(self):
        if messagebox.askyesno("Clear Done", "Remove all completed tasks?"):
            self.todos = [t for t in self.todos if not t["done"]]
            save_todos(self.todos)
            self.refresh()


class TaskDialog(tk.Toplevel):
    """Modal dialog for adding/editing a task."""

    def __init__(self, parent, title, current_title="", current_priority="Medium"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        tk.Label(self, text="Task Title:", bg=BG, fg=TEXT, font=FONT
                 ).pack(padx=24, pady=(20, 4), anchor="w")
        self.title_var = tk.StringVar(value=current_title)
        tk.Entry(self, textvariable=self.title_var, bg=CARD, fg=TEXT,
                 insertbackground=TEXT, font=("Segoe UI", 13), relief="flat",
                 width=32).pack(padx=24, ipady=6)

        tk.Label(self, text="Priority:", bg=BG, fg=TEXT, font=FONT
                 ).pack(padx=24, pady=(12, 4), anchor="w")
        self.priority_var = tk.StringVar(value=current_priority)
        row = tk.Frame(self, bg=BG)
        row.pack(padx=24, fill="x")
        for p in ("High", "Medium", "Low"):
            tk.Radiobutton(row, text=p, variable=self.priority_var, value=p,
                           bg=BG, fg=TEXT, selectcolor=CARD, activebackground=BG,
                           font=FONT).pack(side="left", padx=8)

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=16)
        button(btn_row, "Save", ACCENT, "white", self._save).pack(side="left", padx=6)
        button(btn_row, "Cancel", CARD, TEXT, self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        title = self.title_var.get().strip()
        if not title:
            return
        self.result = {"title": title, "priority": self.priority_var.get()}
        self.destroy()


if __name__ == "__main__":
    ToDoApp().mainloop()
