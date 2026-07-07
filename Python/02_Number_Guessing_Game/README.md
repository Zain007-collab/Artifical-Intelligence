# Number Guessing Game

A number guessing game made with Pygame instead of the usual console version.

## What it does
- The computer picks a random number between 1 and 100
- You get 7 tries to guess it
- Tells you if your guess is too high or too low
- Shows a history of your last 5 guesses
- Win/loss message reveals the correct number
- "New Game" button to play again without restarting the program

## How to run
```bash
pip install -r requirements.txt
python main.py
```

## Controls
- Type a number, then press `Enter` (or click GUESS) to submit
- `Backspace` to fix a typo
- `Escape` to quit

## What I practiced
- Using a `while` loop for the main game loop — this was my first time working with Pygame
- `random.randint` to pick the secret number
- Keeping game state in a small class instead of a bunch of loose variables
- Drawing shapes and text on screen and handling mouse/keyboard events

## Project structure
```
02_Number_Guessing_Game/
├── main.py
├── README.md
└── requirements.txt
```
