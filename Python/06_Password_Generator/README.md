# Password Generator

Generates random passwords using Python's `secrets` module (not `random`, since that's not secure enough for passwords).

## What it does
- Adjustable length (6 to 64 characters)
- Toggle uppercase / lowercase / digits / symbols
- Exclude specific characters (handy for avoiding `0O1lI`)
- Shows a strength rating: Weak → Very Strong
- Copy to clipboard in one click
- Saves generated passwords to a history (last 50)

## How to run
```bash
pip install -r requirements.txt
python main.py
```

## What I practiced
- Using `secrets.choice` and `secrets.randbelow` instead of `random` for actual cryptographic randomness
- Making sure at least one character from each selected type shows up in the password
- A simple scoring function to rate password strength
- Tkinter's `Scale` slider and clipboard access via `pyperclip`

## Project structure
```
06_Password_Generator/
├── main.py
├── history.json     ← auto-created
├── README.md
└── requirements.txt
```
