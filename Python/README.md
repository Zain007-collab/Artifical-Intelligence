# Python Projects

A collection of small Python projects I built while learning the language. Each folder is its own project with a simple GUI (mostly Tkinter, one uses Pygame, and one is a web API instead of a desktop app).

## Projects

1. **Calculator** — basic calculator, Tkinter
2. **Number Guessing Game** — guess a number between 1-100, made with Pygame
3. **To-Do List** — task manager with priorities and search, saves to a JSON file
4. **Student Management System** — add/edit/delete student records in a sortable table
5. **Expense Tracker** — track spending by category, with a pie chart
6. **Password Generator** — generates secure random passwords
7. **Weather App** — pulls live weather from the OpenWeatherMap API
8. **Library Management System** — track books, borrowing, and returns
9. **Quiz Application** — multiple choice quiz with scoring and a leaderboard
10. **REST API** — a small task manager API built with FastAPI

## How to run any of them

```bash
cd 01_Calculator
pip install -r requirements.txt
python main.py
```

A few need a bit more setup:
- **Number Guessing Game** needs `pygame` installed
- **Weather App** needs a free API key from https://openweathermap.org/api
- **REST API** isn't a desktop app — run `uvicorn main:app --reload` and open http://127.0.0.1:8000/docs

## Why these exist

Practicing core Python — functions, loops, classes, file I/O, APIs — by building small but complete apps instead of just doing exercises out of a textbook. Every project folder has its own README explaining what it does and what I practiced building it.

Python 3.10+ required.
