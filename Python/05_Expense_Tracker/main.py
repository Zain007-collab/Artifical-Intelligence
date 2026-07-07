"""Expense Tracker — Tkinter GUI with CSV/JSON storage and an optional pie chart."""

import sys
import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

DATA_FILE = Path(__file__).parent / "expenses.json"
CSV_FILE = Path(__file__).parent / "expenses.csv"

BG, SURFACE, CARD = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD, BAD = "#ff9e64", "#9ece6a", "#f7768e"
TEXT, MUTED = "#c0caf5", "#565f89"

CATEGORIES = ["Food", "Transport", "Shopping", "Health",
              "Entertainment", "Bills", "Education", "Other"]
CAT_COLORS = ["#ff9e64", "#7aa2f7", "#9ece6a", "#e0af68",
              "#f7768e", "#7dcfff", "#bb9af7", "#565f89"]


def load_expenses() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_expenses(data: list[dict]):
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "note"])
        writer.writeheader()
        writer.writerows(data)


def new_expense(category: str, amount: float, note: str) -> dict:
    return {
        "id": f"EXP{datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]}",
        "date": date.today().isoformat(),
        "category": category,
        "amount": round(amount, 2),
        "note": note.strip(),
    }


def totals_by_category(expenses: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for e in expenses:
        totals[e["category"]] += e["amount"]
    return dict(totals)


class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("1000x660")
        self.configure(bg=BG)
        self.minsize(800, 550)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.expenses = load_expenses()
        self.month_var = tk.StringVar(value="All")
        self.cat_var = tk.StringVar(value="All")
        self.month_var.trace_add("write", lambda *_: self.refresh())
        self.cat_var.trace_add("write", lambda *_: self.refresh())

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Frame(self, bg=SURFACE, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="Expense Tracker", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        self.total_lbl = tk.Label(header, bg=SURFACE, fg=GOOD, font=("Segoe UI", 14, "bold"))
        self.total_lbl.pack(side="right", padx=20)

        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True)

        left = tk.Frame(paned, bg=BG, width=320)
        right = tk.Frame(paned, bg=BG)
        paned.add(left, minsize=280)
        paned.add(right, minsize=400)

        self._build_form(left)
        if HAS_MPL:
            self._build_chart(left)
        self._build_table(right)

    def _build_form(self, parent):
        form = tk.LabelFrame(parent, text=" Add Expense ", bg=SURFACE, fg=ACCENT,
                              font=("Segoe UI", 12, "bold"), relief="flat", padx=14, pady=10)
        form.pack(fill="x", padx=12, pady=12)

        self.cat_entry = tk.StringVar(value="Food")
        self.amt_entry = tk.StringVar()
        self.note_entry = tk.StringVar()

        for i, (label, var) in enumerate([("Category", self.cat_entry),
                                           ("Amount (PKR)", self.amt_entry),
                                           ("Note", self.note_entry)]):
            tk.Label(form, text=label, bg=SURFACE, fg=MUTED,
                     font=("Segoe UI", 11)).grid(row=i, column=0, sticky="w", pady=4)
            if label == "Category":
                ttk.Combobox(form, textvariable=var, values=CATEGORIES, state="readonly",
                             width=18, font=("Segoe UI", 11)).grid(
                    row=i, column=1, pady=4, padx=(8, 0), sticky="w")
            else:
                tk.Entry(form, textvariable=var, bg=CARD, fg=TEXT, insertbackground=TEXT,
                         font=("Segoe UI", 11), relief="flat", width=20).grid(
                    row=i, column=1, pady=4, padx=(8, 0), ipady=5)

        tk.Button(form, text="Add Expense", bg=ACCENT, fg=BG, font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  command=self.add_expense).grid(row=3, column=0, columnspan=2,
                                                  pady=(12, 4), sticky="ew")

        filters = tk.Frame(parent, bg=BG)
        filters.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(filters, text="Month:", bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(side="left")
        months = ["All"] + sorted({e["date"][:7] for e in self.expenses}, reverse=True)
        ttk.Combobox(filters, textvariable=self.month_var, values=months, width=10,
                     font=("Segoe UI", 11), state="readonly").pack(side="left", padx=4)
        tk.Label(filters, text="Cat:", bg=BG, fg=MUTED,
                 font=("Segoe UI", 11)).pack(side="left", padx=(8, 0))
        ttk.Combobox(filters, textvariable=self.cat_var, values=["All"] + CATEGORIES,
                     width=10, font=("Segoe UI", 11), state="readonly").pack(side="left", padx=4)

    def _build_chart(self, parent):
        self.fig, self.ax = plt.subplots(figsize=(3.2, 2.6), facecolor=SURFACE)
        self.fig.tight_layout(pad=1.2)
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.chart_canvas.get_tk_widget().pack(padx=12, fill="x")

    def _update_chart(self, expenses: list[dict]):
        if not HAS_MPL:
            return
        self.ax.clear()
        totals = totals_by_category(expenses)
        if totals:
            labels, values = list(totals), list(totals.values())
            colors = [CAT_COLORS[CATEGORIES.index(l) % len(CAT_COLORS)]
                      if l in CATEGORIES else MUTED for l in labels]
            _, _, autotexts = self.ax.pie(values, labels=labels, colors=colors,
                                           autopct="%1.0f%%", startangle=140,
                                           textprops={"color": TEXT, "fontsize": 7})
            for at in autotexts:
                at.set_color(BG)
                at.set_fontsize(7)
        self.ax.set_facecolor(SURFACE)
        self.fig.patch.set_facecolor(SURFACE)
        self.chart_canvas.draw()

    def _build_table(self, parent):
        toolbar = tk.Frame(parent, bg=BG, pady=8)
        toolbar.pack(fill="x", padx=8)
        tk.Label(toolbar, text="Expense History", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=8)
        tk.Button(toolbar, text="Delete Selected", bg=BAD, fg="white",
                  font=("Segoe UI", 11), relief="flat", padx=8, pady=4, cursor="hand2",
                  command=self.delete_expense).pack(side="right", padx=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                         foreground=TEXT, rowheight=30, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background=SURFACE, foreground=ACCENT,
                         font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", BG)])

        cols = ("Date", "Category", "Amount", "Note")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, [100, 110, 100, 250]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=(8, 0))

        self.row_ids: dict[str, str] = {}

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.row_ids.clear()

        month, cat = self.month_var.get(), self.cat_var.get()
        filtered = [
            e for e in self.expenses
            if (month == "All" or e["date"].startswith(month))
            and (cat == "All" or e["category"] == cat)
        ]

        for e in sorted(filtered, key=lambda x: x["date"], reverse=True):
            iid = self.tree.insert("", "end", values=(
                e["date"], e["category"], f"PKR {e['amount']:,.0f}", e["note"]))
            self.row_ids[iid] = e["id"]

        self.total_lbl.config(text=f"Total: PKR {sum(e['amount'] for e in filtered):,.0f}")
        self._update_chart(filtered)

    def add_expense(self):
        try:
            amount = float(self.amt_entry.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive amount.")
            return

        self.expenses.append(new_expense(self.cat_entry.get(), amount, self.note_entry.get()))
        save_expenses(self.expenses)
        self.amt_entry.set("")
        self.note_entry.set("")
        self.refresh()

    def delete_expense(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select an expense first.")
            return
        eid = self.row_ids.get(sel[0])
        if eid and messagebox.askyesno("Delete", "Delete this expense?"):
            self.expenses = [e for e in self.expenses if e["id"] != eid]
            save_expenses(self.expenses)
            self.refresh()

    def on_close(self):
        self.quit()
        self.destroy()
        sys.exit(0)
if __name__ == "__main__":
    ExpenseApp().mainloop()
