"""Quiz Application — Tkinter GUI with a multi-screen quiz flow."""

import json
import random
import tkinter as tk
from pathlib import Path
from datetime import datetime

SCORES_FILE = Path(__file__).parent / "scores.json"

BG, CARD, SURFACE = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD, BAD, GOLD, BLUE = "#e0af68", "#9ece6a", "#f7768e", "#e0af68", "#7aa2f7"
TEXT, MUTED = "#c0caf5", "#565f89"

QUESTIONS: list[dict] = [
    {"q": "What does `len([1, 2, 3])` return?", "options": ["2", "3", "4", "1"],
     "answer": "3", "category": "Python", "points": 1},
    {"q": "Which keyword is used to define a function in Python?",
     "options": ["function", "def", "fun", "define"], "answer": "def",
     "category": "Python", "points": 1},
    {"q": "What is the output of `type(3.14)`?",
     "options": ["int", "float", "double", "number"], "answer": "float",
     "category": "Python", "points": 1},
    {"q": "Which of these is a mutable data type?",
     "options": ["tuple", "string", "list", "frozenset"], "answer": "list",
     "category": "Python", "points": 1},
    {"q": "What does `range(5)` produce?",
     "options": ["[1,2,3,4,5]", "[0,1,2,3,4]", "[0,1,2,3,4,5]", "[1,2,3,4]"],
     "answer": "[0,1,2,3,4]", "category": "Python", "points": 1},
    {"q": "What does API stand for?",
     "options": ["Application Programming Interface", "Advanced Program Integration",
                 "Automated Processing Input", "Application Process Index"],
     "answer": "Application Programming Interface", "category": "General", "points": 1},
    {"q": "Which data structure uses LIFO order?",
     "options": ["Queue", "Stack", "Array", "Linked List"], "answer": "Stack",
     "category": "General", "points": 1},
    {"q": "What is Big O notation used for?",
     "options": ["Describing loops", "Algorithm complexity", "Memory addresses", "Syntax rules"],
     "answer": "Algorithm complexity", "category": "General", "points": 1},
    {"q": "Who created Python?",
     "options": ["James Gosling", "Guido van Rossum", "Linus Torvalds", "Dennis Ritchie"],
     "answer": "Guido van Rossum", "category": "CS History", "points": 2},
    {"q": "What year was Python first released?",
     "options": ["1985", "1991", "1998", "2001"], "answer": "1991",
     "category": "CS History", "points": 2},
    {"q": "Which company developed the Python language?",
     "options": ["Microsoft", "Google", "CWI (Netherlands)", "Oracle"],
     "answer": "CWI (Netherlands)", "category": "CS History", "points": 2},
    {"q": "What does OOP stand for?",
     "options": ["Object-Oriented Programming", "Open-Only Protocol",
                 "Operator Overloading Process", "Online Object Protocol"],
     "answer": "Object-Oriented Programming", "category": "General", "points": 1},
    {"q": "What is `bool(0)` in Python?",
     "options": ["True", "False", "None", "Error"], "answer": "False",
     "category": "Python", "points": 2},
    {"q": "What is `2 ** 10` in Python?",
     "options": ["20", "100", "1024", "512"], "answer": "1024",
     "category": "Python", "points": 2},
    {"q": "Which module provides `datetime` in Python?",
     "options": ["time", "datetime", "calendar", "sys"], "answer": "datetime",
     "category": "Python", "points": 1},
]


def build_quiz(n: int = 10, category: str = "All") -> list[dict]:
    pool = QUESTIONS if category == "All" else [q for q in QUESTIONS if q["category"] == category]
    return random.sample(pool, min(n, len(pool)))


def check_answer(question: dict, answer: str) -> bool:
    return answer == question["answer"]


def grade(score: int, total: int) -> tuple[str, str]:
    pct = score / total * 100 if total else 0
    if pct >= 90:
        return "Excellent!", GOOD
    if pct >= 70:
        return "Good Job!", BLUE
    if pct >= 50:
        return "Keep Going!", GOLD
    return "Try Again!", BAD


def load_scores() -> list[dict]:
    if SCORES_FILE.exists():
        try:
            return json.loads(SCORES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_score(name: str, score: int, correct: int, max_pts: int):
    scores = load_scores()
    scores.insert(0, {"name": name, "score": score, "max": max_pts, "correct": correct,
                       "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
    SCORES_FILE.write_text(json.dumps(scores[:20], indent=2), encoding="utf-8")


class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Application")
        self.geometry("800x800")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.quiz: list[dict] = []
        self.idx = 0
        self.score = 0
        self.correct = 0

        self._build_start_screen()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _build_start_screen(self):
        self._clear()

        tk.Label(self, text="Quiz App", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 30, "bold")).pack(pady=(50, 4))
        tk.Label(self, text="Test your Python & CS knowledge", bg=BG, fg=MUTED,
                 font=("Segoe UI", 13)).pack(pady=(0, 30))

        form = tk.Frame(self, bg=CARD, padx=30, pady=24)
        form.pack(padx=60)

        tk.Label(form, text="Your Name", bg=CARD, fg=TEXT, font=("Segoe UI", 13)).pack(anchor="w")
        self.name_var = tk.StringVar(value="Player 1")
        tk.Entry(form, textvariable=self.name_var, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                 font=("Segoe UI", 13), relief="flat", width=30).pack(ipady=7, pady=(4, 14))

        tk.Label(form, text="Category", bg=CARD, fg=TEXT, font=("Segoe UI", 13)).pack(anchor="w")
        self.cat_var = tk.StringVar(value="All")
        cat_frame = tk.Frame(form, bg=CARD)
        cat_frame.pack(fill="x", pady=(4, 14))
        for cat in ["All"] + sorted({q["category"] for q in QUESTIONS}):
            tk.Radiobutton(cat_frame, text=cat, variable=self.cat_var, value=cat, bg=CARD,
                           fg=TEXT, selectcolor=SURFACE, activebackground=CARD,
                           font=("Segoe UI", 12), cursor="hand2").pack(side="left", padx=6)

        tk.Label(form, text="Number of Questions", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13)).pack(anchor="w")
        self.num_var = tk.IntVar(value=10)
        tk.Scale(form, from_=5, to=15, orient="horizontal", variable=self.num_var, bg=CARD,
                 fg=TEXT, troughcolor=SURFACE, activebackground=ACCENT, highlightthickness=0,
                 length=280).pack(pady=(4, 16))

        tk.Button(form, text="Start Quiz", bg=ACCENT, fg=BG, font=("Segoe UI", 14, "bold"),
                  relief="flat", padx=20, pady=10, cursor="hand2", command=self._start).pack()

        scores = load_scores()
        if scores:
            tk.Label(self, text="Recent Scores", bg=BG, fg=MUTED,
                     font=("Segoe UI", 12)).pack(pady=(20, 4))
            for s in scores[:5]:
                pct = round(s["score"] / s["max"] * 100) if s["max"] else 0
                tk.Label(self, text=f"  {s['name']:<16} {s['score']}/{s['max']}pts  "
                                     f"({pct}%)  {s['date']}",
                         bg=BG, fg=TEXT, font=("Consolas", 11)).pack()

    def _start(self):
        self.quiz = build_quiz(self.num_var.get(), self.cat_var.get())
        self.idx = 0
        self.score = 0
        self.correct = 0
        self.name = self.name_var.get().strip() or "Player"
        self._build_question_screen()

    def _build_question_screen(self):
        self._clear()

        q = self.quiz[self.idx]
        total = len(self.quiz)

        top = tk.Frame(self, bg=BG, pady=6)
        top.pack(fill="x", padx=24)
        tk.Label(top, text=f"Q {self.idx + 1} of {total}  •  {q['category']}  •  "
                            f"{q['points']}pt{'s' if q['points'] > 1 else ''}",
                 bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(side="left")
        tk.Label(top, text=f"Score: {self.score}", bg=BG, fg=GOLD,
                 font=("Segoe UI", 12, "bold")).pack(side="right")

        bar = tk.Frame(self, bg=SURFACE, height=6)
        bar.pack(fill="x", padx=24, pady=(0, 16))
        tk.Frame(bar, bg=ACCENT, height=6, width=int((self.idx / total) * (620 - 48))
                 ).pack(side="left")

        card = tk.Frame(self, bg=CARD, padx=24, pady=20)
        card.pack(fill="x", padx=24)
        tk.Label(card, text=q["q"], bg=CARD, fg=TEXT, font=("Segoe UI", 15),
                 wraplength=520, justify="left").pack(anchor="w")

        options_frame = tk.Frame(self, bg=BG)
        options_frame.pack(fill="x", padx=24, pady=12)

        options = q["options"][:]
        random.shuffle(options)
        self.opt_buttons: dict[str, tk.Button] = {}
        self.answered = False

        for opt in options:
            btn = tk.Button(options_frame, text=opt, bg=SURFACE, fg=TEXT,
                            font=("Segoe UI", 13), relief="flat", anchor="w", padx=16, pady=10,
                            cursor="hand2", wraplength=490, justify="left",
                            command=lambda o=opt: self._answer(o))
            btn.pack(fill="x", pady=4)
            self.opt_buttons[opt] = btn
            btn.bind("<Enter>", lambda e, b=btn: None if self.answered else b.config(bg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: None if self.answered else b.config(bg=SURFACE))

        nav = tk.Frame(self, bg=BG, pady=8)
        nav.pack(fill="x", padx=24)
        self.feedback_lbl = tk.Label(nav, text="", bg=BG, font=("Segoe UI", 13, "bold"))
        self.feedback_lbl.pack(side="left")
        self.next_btn = tk.Button(nav, text="Next →", bg=SURFACE, fg=TEXT,
                                   font=("Segoe UI", 12, "bold"), relief="flat", padx=16, pady=6,
                                   cursor="hand2", state="disabled", command=self._next)
        self.next_btn.pack(side="right")

    def _answer(self, chosen: str):
        if self.answered:
            return
        self.answered = True

        q = self.quiz[self.idx]
        correct = check_answer(q, chosen)

        for opt, btn in self.opt_buttons.items():
            btn.config(cursor="arrow")
            if opt == q["answer"]:
                btn.config(bg=GOOD, fg=BG)
            elif opt == chosen:
                btn.config(bg=BAD, fg="white")

        if correct:
            self.score += q["points"]
            self.correct += 1
            self.feedback_lbl.config(text="Correct!", fg=GOOD)
        else:
            self.feedback_lbl.config(text=f"Answer: {q['answer']}", fg=BAD)

        self.next_btn.config(state="normal", bg=ACCENT)

    def _next(self):
        self.idx += 1
        if self.idx < len(self.quiz):
            self._build_question_screen()
        else:
            self._build_results_screen()

    def _build_results_screen(self):
        self._clear()
        max_pts = sum(q["points"] for q in self.quiz)
        label, color = grade(self.score, max_pts)
        save_score(self.name, self.score, self.correct, max_pts)

        tk.Label(self, text=label, bg=BG, fg=color, font=("Segoe UI", 32, "bold")
                 ).pack(pady=(50, 8))
        tk.Label(self, text=f"{self.name}'s Result", bg=BG, fg=MUTED,
                 font=("Segoe UI", 14)).pack()

        panel = tk.Frame(self, bg=CARD, padx=40, pady=24)
        panel.pack(padx=80, pady=24)

        pct = round(self.score / max_pts * 100) if max_pts else 0
        for label, value, color_ in [
            ("Score", f"{self.score} / {max_pts} pts", GOLD),
            ("Correct", f"{self.correct} / {len(self.quiz)}", GOOD),
            ("Accuracy", f"{pct}%", BLUE),
        ]:
            row = tk.Frame(panel, bg=CARD)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 13), width=10,
                     anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=CARD, fg=color_,
                     font=("Segoe UI", 15, "bold")).pack(side="left", padx=16)

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="Play Again", bg=ACCENT, fg=BG, font=("Segoe UI", 13, "bold"),
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  command=self._start).pack(side="left", padx=8)
        tk.Button(btn_row, text="Main Menu", bg=SURFACE, fg=TEXT, font=("Segoe UI", 13),
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  command=self._build_start_screen).pack(side="left", padx=8)


if __name__ == "__main__":
    QuizApp().mainloop()
