# Quiz Application

A multiple-choice quiz about Python and general CS trivia, with scoring and a leaderboard.

## What it does
- 15 questions across 3 categories: Python, General, CS History
- Pick how many questions (5-15) and which category
- Some questions are worth more points than others
- Instant feedback after each answer, shows the correct one if you got it wrong
- Grades you at the end: Excellent / Good Job / Keep Going / Try Again
- Keeps a leaderboard of your last few attempts in `scores.json`

## How to run
```bash
python main.py
```
No extra installs needed — just the Python standard library.

## What I practiced
- Storing each question as a dictionary (question, options, answer, category, points)
- `random.sample` to pick unique questions and `random.shuffle` to randomize answer order
- Building a multi-screen app in Tkinter (start screen → question screen → results screen) by clearing and rebuilding widgets
- Simple scoring/grading logic

## Project structure
```
09_Quiz_Application/
├── main.py
├── scores.json      ← auto-created
├── README.md
└── requirements.txt
```
