"""Calculator — Tkinter GUI with keyboard support."""

import tkinter as tk

BG, CARD = "#1a1b26", "#20222f"
NUM, NUM_HOVER = "#24273a", "#2f3350"
OP, OP_HOVER = "#3b4261", "#4a5178"
FN, FN_HOVER = "#292e42", "#3b4261"
EQ, EQ_HOVER = "#9ece6a", "#82ac57"
TEXT, MUTED = "#c0caf5", "#565f89"

BUTTONS = [
    ["C", "⌫", "%", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["±", "0", ".", "="],
]

STYLES = {
    "=": (EQ, EQ_HOVER, BG),
    **{k: (OP, OP_HOVER, TEXT) for k in "/*-+%"},
    **{k: (FN, FN_HOVER, TEXT) for k in ("C", "⌫", "±")},
}


def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def calculate(expression: str) -> float:
    """Safely evaluate a math expression."""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        raise ValueError("Invalid characters in expression")
    return eval(expression)


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.expression = ""

        self._build_display()
        self._build_keypad()
        self._bind_keys()

    def _build_display(self):
        frame = tk.Frame(self, bg=CARD, padx=16, pady=12)
        frame.pack(fill="x", padx=16, pady=(16, 8))

        self.history_var = tk.StringVar()
        tk.Label(frame, textvariable=self.history_var, bg=CARD, fg=MUTED,
                 font=("Consolas", 11), anchor="e").pack(fill="x")

        self.display_var = tk.StringVar(value="0")
        tk.Label(frame, textvariable=self.display_var, bg=CARD, fg=TEXT,
                 font=("Consolas", 28, "bold"), anchor="e").pack(fill="x")

    def _build_keypad(self):
        grid = tk.Frame(self, bg=BG)
        grid.pack(padx=16, pady=(0, 16))

        for r, row in enumerate(BUTTONS):
            for c, label in enumerate(row):
                bg, hover, fg = STYLES.get(label, (NUM, NUM_HOVER, TEXT))
                btn = tk.Button(
                    grid, text=label, width=5, height=2, bg=bg, fg=fg,
                    activebackground=hover, activeforeground=fg,
                    font=("Segoe UI", 14, "bold"), relief="flat", cursor="hand2",
                    command=lambda l=label: self._press(l),
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
                btn.bind("<Leave>", lambda e, b=btn, o=bg: b.config(bg=o))

    def _bind_keys(self):
        for key in "0123456789+-*/.%":
            self.bind(key, lambda e, k=key: self._press(k))
        self.bind("<Return>", lambda e: self._press("="))
        self.bind("<BackSpace>", lambda e: self._press("⌫"))
        self.bind("<Escape>", lambda e: self._press("C"))

    def _press(self, label: str):
        if label == "C":
            self.expression = ""
            self.history_var.set("")
            self.display_var.set("0")
        elif label == "⌫":
            self.expression = self.expression[:-1]
            self.display_var.set(self.expression or "0")
        elif label == "±":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            elif self.expression:
                self.expression = "-" + self.expression
            self.display_var.set(self.expression or "0")
        elif label == "%":
            self._try(lambda: calculate(self.expression) / 100)
        elif label == "=":
            self._equals()
        else:
            self.expression += label
            self.display_var.set(self.expression)

    def _try(self, compute):
        try:
            self.expression = str(compute())
            self.display_var.set(self.expression)
        except Exception:
            self.display_var.set("Error")
            self.expression = ""

    def _equals(self):
        try:
            result = calculate(self.expression)
            result_str = str(int(result)) if result == int(result) else str(result)
            self.history_var.set(f"{self.expression} = {result_str}")
            self.expression = result_str
            self.display_var.set(result_str)
        except ZeroDivisionError:
            self.display_var.set("÷0 Error")
            self.expression = ""
        except Exception:
            self.display_var.set("Error")
            self.expression = ""


if __name__ == "__main__":
    CalculatorApp().mainloop()
