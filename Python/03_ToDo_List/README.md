# To-Do List

A task manager app with priorities, search, and filtering — saves everything to a JSON file so your list is still there next time you open it.

## What it does
- Add, edit, and delete tasks
- Set a priority: High / Medium / Low
- Check tasks off as done (shows with a strikethrough)
- Filter by All / Active / Done
- Search tasks as you type
- "Clear Done" button to clean up finished tasks
- Saves automatically to `todos.json`

## How to run
```bash
python main.py
```
No extra installs needed — just the Python standard library.

## What I practiced
- Reading and writing JSON files with `pathlib`
- Storing tasks as a list of dictionaries and filtering/searching through it
- Basic CRUD (Create, Read, Update, Delete)
- Tkinter Canvas scrolling and popup (`Toplevel`) dialogs

## Project structure
```
03_ToDo_List/
├── main.py
├── todos.json     ← auto-created on first run
├── README.md
└── requirements.txt
```
