# Student Management System

A desktop app to keep track of student records — add, edit, delete, search, and sort.

## What it does
- Add / edit / delete students (name, age, course, GPA)
- Click a column header to sort by it
- Search by name, ID, or course
- GPA is color coded: green (3.5+), yellow (2.5+), red (below that)
- Quick stats bar: average GPA, most popular course, total students
- Saves to `students.json`

## How to run
```bash
python main.py
```
No extra installs needed — just the Python standard library.

## What I practiced
- A small `StudentDB` class to keep the data logic (`add`, `update`, `delete`, `get`, `search`) separate from the UI
- Storing records as a dictionary of `id -> student`
- `ttk.Treeview` for a sortable table, styled so it doesn't look like default Tkinter
- Basic input validation (e.g. GPA has to be between 0 and 4)

## Project structure
```
04_Student_Management_System/
├── main.py
├── students.json     ← auto-created
├── README.md
└── requirements.txt
```
