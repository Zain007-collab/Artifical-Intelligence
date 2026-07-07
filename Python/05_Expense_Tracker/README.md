# Expense Tracker

Tracks personal expenses by category, with a pie chart to see where the money's going.

## What it does
- Add an expense with category, amount, and a note
- Filter by month and category
- Pie chart breakdown of spending per category (needs matplotlib)
- Delete an expense
- Running total shown at the top
- Saves to both `expenses.json` and `expenses.csv`

## How to run
```bash
pip install -r requirements.txt
python main.py
```
Matplotlib is optional — the app still works without it, you just won't see the chart.

## What I practiced
- Exporting the same data to both JSON and CSV
- Using `collections.defaultdict` to sum expenses per category
- Embedding a matplotlib chart inside a Tkinter window
- Tkinter's `PanedWindow` for a resizable split layout

## Project structure
```
05_Expense_Tracker/
├── main.py
├── expenses.json    ← auto-created
├── expenses.csv     ← auto-created (export)
├── README.md
└── requirements.txt
```
