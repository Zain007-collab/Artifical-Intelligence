"""Library Management System — OOP + Tkinter GUI with JSON persistence."""

from __future__ import annotations
import json
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional

DATA_FILE = Path(__file__).parent / "library.json"

BG, SURFACE, CARD = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD, BAD, GOLD = "#bb9af7", "#9ece6a", "#f7768e", "#e0af68"
TEXT, MUTED = "#c0caf5", "#565f89"


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    genre: str
    year: int
    copies: int = 1
    available: int = 1

    def is_available(self) -> bool:
        return self.available > 0

    def borrow(self) -> bool:
        if self.available > 0:
            self.available -= 1
            return True
        return False

    def return_book(self) -> bool:
        if self.available < self.copies:
            self.available += 1
            return True
        return False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Book":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class BorrowRecord:
    record_id: str
    isbn: str
    member_name: str
    borrow_date: str
    due_date: str
    return_date: Optional[str] = None

    @property
    def is_returned(self) -> bool:
        return self.return_date is not None

    @property
    def is_overdue(self) -> bool:
        return not self.is_returned and date.today() > date.fromisoformat(self.due_date)

    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        return (date.today() - date.fromisoformat(self.due_date)).days

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "BorrowRecord":
        return cls(**d)


class Library:
    """Central library object managing books and borrow records."""

    def __init__(self, path: Path):
        self._path = path
        self.books: dict[str, Book] = {}
        self.records: dict[str, BorrowRecord] = {}
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                self.books = {k: Book.from_dict(v) for k, v in raw.get("books", {}).items()}
                self.records = {k: BorrowRecord.from_dict(v)
                                for k, v in raw.get("records", {}).items()}
            except Exception:
                pass

    def _save(self):
        data = {
            "books": {k: v.to_dict() for k, v in self.books.items()},
            "records": {k: v.to_dict() for k, v in self.records.items()},
        }
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_book(self, book: Book):
        if book.isbn in self.books:
            self.books[book.isbn].copies += book.copies
            self.books[book.isbn].available += book.copies
        else:
            self.books[book.isbn] = book
        self._save()

    def remove_book(self, isbn: str) -> bool:
        book = self.books.get(isbn)
        if book and book.available == book.copies:
            del self.books[isbn]
            self._save()
            return True
        return False

    def update_book(self, isbn: str, **fields):
        if isbn in self.books:
            for k, v in fields.items():
                setattr(self.books[isbn], k, v)
            self._save()

    def search_books(self, query: str) -> list[Book]:
        q = query.lower()
        return [b for b in self.books.values()
                if q in b.title.lower() or q in b.author.lower()
                or q in b.isbn or q in b.genre.lower()]

    def borrow(self, isbn: str, member: str, days: int = 14) -> BorrowRecord | None:
        book = self.books.get(isbn)
        if not book or not book.borrow():
            return None
        rid = f"BRW{datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]}"
        record = BorrowRecord(
            record_id=rid, isbn=isbn, member_name=member,
            borrow_date=date.today().isoformat(),
            due_date=(date.today() + timedelta(days=days)).isoformat(),
        )
        self.records[rid] = record
        self._save()
        return record

    def return_book(self, record_id: str) -> bool:
        record = self.records.get(record_id)
        if not record or record.is_returned:
            return False
        record.return_date = date.today().isoformat()
        self.books[record.isbn].return_book()
        self._save()
        return True

    def active_borrows(self) -> list[BorrowRecord]:
        return [r for r in self.records.values() if not r.is_returned]

    def overdue(self) -> list[BorrowRecord]:
        return [r for r in self.records.values() if r.is_overdue]

    def stats(self) -> dict:
        return {
            "total_books": len(self.books),
            "borrowed": sum(b.copies - b.available for b in self.books.values()),
            "overdue": len(self.overdue()),
        }


lib = Library(DATA_FILE)


def style_treeview():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background=CARD, fieldbackground=CARD,
                     foreground=TEXT, rowheight=30, font=("Segoe UI", 11))
    style.configure("Treeview.Heading", background=SURFACE, foreground=ACCENT,
                     font=("Segoe UI", 11, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", BG)])


def make_tree(parent, columns: list[tuple[str, int]]) -> ttk.Treeview:
    """Build a Treeview + vertical scrollbar pair from (label, width) columns."""
    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    names = [c for c, _ in columns]
    tree = ttk.Treeview(frame, columns=names, show="headings", selectmode="browse")
    for name, width in columns:
        tree.heading(name, text=name)
        tree.column(name, width=width, anchor="center")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    return tree


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1020x660")
        self.configure(bg=BG)
        self.minsize(900, 560)

        self._build_ui()
        self.refresh_books()

    def _build_ui(self):
        header = tk.Frame(self, bg=SURFACE, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="Library Management System", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        self.stat_lbl = tk.Label(header, bg=SURFACE, fg=MUTED, font=("Segoe UI", 11))
        self.stat_lbl.pack(side="right", padx=20)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=SURFACE, foreground=MUTED,
                         font=("Segoe UI", 12), padding=[14, 6])
        style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.books_tab = tk.Frame(notebook, bg=BG)
        self.borrow_tab = tk.Frame(notebook, bg=BG)
        self.returns_tab = tk.Frame(notebook, bg=BG)
        notebook.add(self.books_tab, text="Books")
        notebook.add(self.borrow_tab, text="Borrow")
        notebook.add(self.returns_tab, text="Returns & Overdue")
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        style_treeview()
        self._build_books_tab()
        self._build_borrow_tab()
        self._build_returns_tab()

    # ── Books tab ──────────────────────────────────────────────────────────

    def _build_books_tab(self):
        tab = self.books_tab
        toolbar = tk.Frame(tab, bg=BG, pady=8)
        toolbar.pack(fill="x", padx=12)

        self.book_search = tk.StringVar()
        self.book_search.trace_add("write", lambda *_: self.refresh_books())
        tk.Entry(toolbar, textvariable=self.book_search, bg=CARD, fg=TEXT,
                 insertbackground=TEXT, font=("Segoe UI", 12), relief="flat",
                 width=22).pack(side="left", padx=4, ipady=5)

        for text, cmd, color in [("Add Book", self.add_book, GOOD),
                                  ("Edit", self.edit_book, GOLD),
                                  ("Remove", self.remove_book, BAD)]:
            tk.Button(toolbar, text=text, bg=color, fg=BG, font=("Segoe UI", 11, "bold"),
                      relief="flat", padx=8, pady=4, cursor="hand2",
                      command=cmd).pack(side="left", padx=4)

        self.book_tree = make_tree(tab, [
            ("ISBN", 120), ("Title", 200), ("Author", 150),
            ("Genre", 100), ("Year", 60), ("Copies", 70), ("Available", 80),
        ])

    def refresh_books(self, _=None):
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)

        query = self.book_search.get()
        books = lib.search_books(query) if query else list(lib.books.values())

        self.book_tree.tag_configure("avail", foreground=GOOD)
        self.book_tree.tag_configure("unavail", foreground=BAD)
        for b in sorted(books, key=lambda x: x.title):
            self.book_tree.insert("", "end", iid=b.isbn,
                values=(b.isbn, b.title, b.author, b.genre, b.year, b.copies, b.available),
                tags=("avail" if b.is_available() else "unavail",))

        s = lib.stats()
        self.stat_lbl.config(text=f"Books: {s['total_books']}  |  "
                                   f"Borrowed: {s['borrowed']}  |  Overdue: {s['overdue']}")

    def _selected_isbn(self) -> str | None:
        sel = self.book_tree.selection()
        return sel[0] if sel else None

    def add_book(self):
        dialog = BookDialog(self, "Add Book")
        self.wait_window(dialog)
        if dialog.result:
            lib.add_book(Book(**dialog.result))
            self.refresh_books()

    def edit_book(self):
        isbn = self._selected_isbn()
        if not isbn:
            messagebox.showinfo("Select", "Select a book first.")
            return
        dialog = BookDialog(self, "Edit Book", asdict(lib.books[isbn]))
        self.wait_window(dialog)
        if dialog.result:
            lib.update_book(isbn, **{k: v for k, v in dialog.result.items() if k != "isbn"})
            self.refresh_books()

    def remove_book(self):
        isbn = self._selected_isbn()
        if not isbn:
            messagebox.showinfo("Select", "Select a book first.")
            return
        if lib.remove_book(isbn):
            self.refresh_books()
        else:
            messagebox.showerror("Cannot Remove",
                                  "Book has active borrows. Return all copies first.")

    # ── Borrow tab ────────────────────────────────────────────────────────

    def _build_borrow_tab(self):
        tab = self.borrow_tab
        form = tk.Frame(tab, bg=SURFACE, padx=24, pady=18)
        form.pack(padx=40, pady=30)

        tk.Label(form, text="Borrow a Book", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 16))

        self.borrow_isbn = tk.StringVar()
        self.borrow_member = tk.StringVar()
        self.borrow_days = tk.StringVar(value="14")
        fields = [("ISBN", self.borrow_isbn), ("Member Name", self.borrow_member),
                  ("Loan Period (days)", self.borrow_days)]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label, bg=SURFACE, fg=TEXT,
                     font=("Segoe UI", 12)).grid(row=i + 1, column=0, sticky="w", pady=6)
            tk.Entry(form, textvariable=var, bg=CARD, fg=TEXT, insertbackground=TEXT,
                     font=("Segoe UI", 12), relief="flat", width=26).grid(
                row=i + 1, column=1, pady=6, padx=(12, 0), ipady=6)

        tk.Button(form, text="Borrow Book", bg=ACCENT, fg="white", font=("Segoe UI", 13, "bold"),
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  command=self.do_borrow).grid(row=4, column=0, columnspan=2, pady=16, sticky="ew")

        self.borrow_result = tk.Label(form, text="", bg=SURFACE, font=("Segoe UI", 11))
        self.borrow_result.grid(row=5, column=0, columnspan=2)

        tk.Label(tab, text="Active Borrows", bg=BG, fg=MUTED,
                 font=("Segoe UI", 13)).pack(padx=12, anchor="w")
        self.borrow_tree = make_tree(tab, [
            ("Record ID", 140), ("ISBN", 100), ("Title", 180),
            ("Member", 130), ("Due Date", 100), ("Status", 80),
        ])

    def do_borrow(self):
        isbn = self.borrow_isbn.get().strip()
        member = self.borrow_member.get().strip()
        try:
            days = int(self.borrow_days.get())
        except ValueError:
            days = 14

        if not isbn or not member:
            self.borrow_result.config(text="Fill in all fields.", fg=BAD)
            return

        book = lib.books.get(isbn)
        if not book:
            self.borrow_result.config(text=f"ISBN {isbn} not found.", fg=BAD)
            return

        record = lib.borrow(isbn, member, days)
        if record:
            self.borrow_result.config(text=f"Borrowed '{book.title}' — due {record.due_date}",
                                       fg=GOOD)
            self.borrow_isbn.set("")
            self.borrow_member.set("")
            self.refresh_books()
            self.refresh_borrows()
        else:
            self.borrow_result.config(text="No copies available.", fg=BAD)

    def refresh_borrows(self):
        for row in self.borrow_tree.get_children():
            self.borrow_tree.delete(row)

        self.borrow_tree.tag_configure("overdue", foreground=BAD)
        self.borrow_tree.tag_configure("ok", foreground=GOOD)
        for r in lib.active_borrows():
            title = lib.books[r.isbn].title if r.isbn in lib.books else r.isbn
            status = f"{r.days_overdue}d late" if r.is_overdue else "On time"
            self.borrow_tree.insert("", "end", iid=r.record_id,
                values=(r.record_id, r.isbn, title, r.member_name, r.due_date, status),
                tags=("overdue" if r.is_overdue else "ok",))

    # ── Returns tab ───────────────────────────────────────────────────────

    def _build_returns_tab(self):
        tab = self.returns_tab
        form = tk.Frame(tab, bg=SURFACE, padx=24, pady=16)
        form.pack(padx=40, pady=20)

        tk.Label(form, text="Return a Book", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tk.Label(form, text="Record ID:", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", pady=6)
        self.return_id = tk.StringVar()
        tk.Entry(form, textvariable=self.return_id, bg=CARD, fg=TEXT, insertbackground=TEXT,
                 font=("Segoe UI", 12), relief="flat", width=28).grid(
            row=1, column=1, pady=6, padx=(12, 0), ipady=6)

        tk.Button(form, text="Return Book", bg=GOOD, fg=BG, font=("Segoe UI", 13, "bold"),
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  command=self.do_return).grid(row=2, column=0, columnspan=2, pady=12, sticky="ew")

        self.return_result = tk.Label(form, text="", bg=SURFACE, font=("Segoe UI", 11))
        self.return_result.grid(row=3, column=0, columnspan=2)

        tk.Label(tab, text="Overdue Books", bg=BG, fg=BAD,
                 font=("Segoe UI", 13, "bold")).pack(padx=12, anchor="w")
        self.overdue_tree = make_tree(tab, [
            ("Record ID", 140), ("ISBN", 100), ("Title", 180),
            ("Member", 130), ("Due Date", 100), ("Days Overdue", 110),
        ])

    def do_return(self):
        rid = self.return_id.get().strip()
        if not rid:
            self.return_result.config(text="Enter a Record ID.", fg=BAD)
            return
        if lib.return_book(rid):
            self.return_result.config(text="Book returned successfully!", fg=GOOD)
            self.return_id.set("")
            self.refresh_books()
            self.refresh_borrows()
            self.refresh_overdue()
        else:
            self.return_result.config(text="Record not found or already returned.", fg=BAD)

    def refresh_overdue(self):
        for row in self.overdue_tree.get_children():
            self.overdue_tree.delete(row)
        for r in lib.overdue():
            title = lib.books[r.isbn].title if r.isbn in lib.books else r.isbn
            self.overdue_tree.insert("", "end", values=(
                r.record_id, r.isbn, title, r.member_name, r.due_date, r.days_overdue))

    def _on_tab_change(self, event):
        idx = event.widget.index("current")
        if idx == 1:
            self.refresh_borrows()
        elif idx == 2:
            self.refresh_borrows()
            self.refresh_overdue()


class BookDialog(tk.Toplevel):
    GENRES = ["Fiction", "Non-Fiction", "Science", "History", "Technology",
              "Biography", "Philosophy", "Children", "Other"]

    def __init__(self, parent, title: str, data: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        data = data or {}

        tk.Label(self, text=title, bg=BG, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(pady=(16, 10))

        form = tk.Frame(self, bg=BG, padx=30)
        form.pack()

        self.vars: dict[str, tk.StringVar] = {}
        for row, (label, key, default) in enumerate([
            ("ISBN", "isbn", ""), ("Title", "title", ""), ("Author", "author", ""),
            ("Year", "year", ""), ("Copies", "copies", "1"),
        ]):
            tk.Label(form, text=label, bg=BG, fg=TEXT, font=("Segoe UI", 12), width=10,
                     anchor="w").grid(row=row, column=0, pady=6, sticky="w")
            var = tk.StringVar(value=str(data.get(key, default)))
            self.vars[key] = var
            entry = tk.Entry(form, textvariable=var, bg=CARD, fg=TEXT, insertbackground=TEXT,
                              font=("Segoe UI", 12), relief="flat", width=24)
            entry.grid(row=row, column=1, pady=6, padx=(10, 0), ipady=5)
            if key == "isbn" and data:
                entry.config(state="disabled")

        tk.Label(form, text="Genre", bg=BG, fg=TEXT, font=("Segoe UI", 12), width=10,
                 anchor="w").grid(row=5, column=0, pady=6, sticky="w")
        self.genre_var = tk.StringVar(value=data.get("genre", "Fiction"))
        ttk.Combobox(form, textvariable=self.genre_var, values=self.GENRES, state="readonly",
                     font=("Segoe UI", 12), width=22).grid(row=5, column=1, pady=6, padx=(10, 0))

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=14)
        tk.Button(btn_row, text="Save", bg=ACCENT, fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=self._save).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel", bg=CARD, fg=TEXT, font=("Segoe UI", 12), relief="flat",
                  padx=16, pady=6, cursor="hand2", command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        try:
            isbn = self.vars["isbn"].get().strip()
            title = self.vars["title"].get().strip()
            author = self.vars["author"].get().strip()
            if not all([isbn, title, author]):
                raise ValueError("ISBN, Title, and Author are required.")
            copies = int(self.vars["copies"].get())
            self.result = {
                "isbn": isbn, "title": title, "author": author,
                "genre": self.genre_var.get(), "year": int(self.vars["year"].get()),
                "copies": copies, "available": copies,
            }
        except ValueError as e:
            messagebox.showerror("Validation", str(e) or "Invalid year or copies.", parent=self)
            return
        self.destroy()


if __name__ == "__main__":
    LibraryApp().mainloop()
