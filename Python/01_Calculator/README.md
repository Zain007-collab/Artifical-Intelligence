# Calculator

A simple calculator app built with Python and Tkinter.

## What it does
- Basic math: add, subtract, multiply, divide
- Percent (%) and +/- sign toggle
- Clear and backspace buttons
- Shows the last calculation above the current one
- Works with the keyboard, not just by clicking buttons

## How to run
```bash
python main.py
```
No extra installs needed — it only uses Python's built-in `tkinter`.

## Keyboard shortcuts
| Key                  | What it does             |
|----------------------|--------------------------|
| `0-9`, `+ - * / % .` | type into the expression |
| `Enter`              | calculate                |
| `Backspace`          | delete last character    |
| `Escape`             | clear everything         |

## What I practiced
- Writing small pure functions (`add`, `subtract`, `multiply`, `divide`)
- Using if/elif to route button clicks to the right action
- Building a Tkinter class that manages both state and the UI
- Handling errors like dividing by zero without crashing the app

## Project structure
```
01_Calculator/
├── main.py
├── README.md
└── requirements.txt
```
