# Library Management System

Manages a small library — books, who borrowed what, and what's overdue.

## What it does
- **Books tab**   — add, edit, remove books; search by title/author/genre/ISBN
- **Borrow tab**  — lend a book to a member, see all active borrows
- **Returns tab** — return a book by its record ID, see what's overdue and by how many days
- Available books shown in green, unavailable in red
- Saves everything to `library.json`

## How to run
```bash
python main.py
```
No extra installs needed — just the Python standard library.

## How to use it
1. Add some books in the Books tab
2. Go to the Borrow tab, enter the ISBN and a member name to lend it out
3. To return it, go to the Returns tab and enter the Record ID shown in the borrow list
4. Anything overdue shows up automatically in red

## What I practiced
- Using `@dataclass` for the `Book` and `BorrowRecord` models instead of plain dictionaries
- A `Library` class that owns all the borrowing/returning logic
- `ttk.Notebook` to build a tabbed interface
- Date math with `datetime`/`timedelta` for due dates and overdue tracking

## Project structure
```
08_Library_Management_System/
├── main.py
├── library.json     ← auto-created
├── README.md
└── requirements.txt
```
