"""Password Generator — Tkinter GUI using the `secrets` module for randomness."""

import json
import string
import secrets
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

import pyperclip

HISTORY_FILE = Path(__file__).parent / "history.json"

BG, CARD, SURFACE = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD = "#f7768e", "#9ece6a"
TEXT, MUTED = "#c0caf5", "#565f89"

CHARSETS = {
    "uppercase": string.ascii_uppercase,
    "lowercase": string.ascii_lowercase,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{}|;:,.<>?",
}


def generate_password(length: int, use: dict[str, bool], exclude: str = "") -> str:
    """Generate a cryptographically secure password."""
    pool = ""
    required: list[str] = []

    for key, chars in CHARSETS.items():
        if use.get(key):
            cleaned = "".join(c for c in chars if c not in exclude)
            if cleaned:
                pool += cleaned
                required.append(secrets.choice(cleaned))

    if not pool:
        raise ValueError("Select at least one character type.")

    password = required + [secrets.choice(pool) for _ in range(length - len(required))]
    for i in range(len(password) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password[i], password[j] = password[j], password[i]

    return "".join(password)


def strength(password: str) -> tuple[str, str]:
    """Return (label, color) based on password composition."""
    score = sum([
        len(password) >= 12, len(password) >= 16,
        any(c.isupper() for c in password), any(c.islower() for c in password),
        any(c.isdigit() for c in password),
        any(c in CHARSETS["symbols"] for c in password),
    ])
    if score <= 2:
        return "Weak", "#f7768e"
    if score <= 4:
        return "Fair", "#e0af68"
    if score == 5:
        return "Strong", "#9ece6a"
    return "Very Strong", "#73daca"


def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_to_history(pwd: str):
    hist = load_history()
    hist.insert(0, {"password": pwd, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
    HISTORY_FILE.write_text(json.dumps(hist[:50], indent=2), encoding="utf-8")


class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")
        self.geometry("560x680")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.length_var = tk.IntVar(value=16)
        self.use = {k: tk.BooleanVar(value=True) for k in CHARSETS}
        self.use["symbols"].set(False)
        self.exclude_var = tk.StringVar()
        self.pwd_var = tk.StringVar()

        self._build_ui()
        self.generate()

    def _build_ui(self):
        tk.Label(self, text="Password Generator", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 22, "bold")).pack(pady=(24, 4))
        tk.Label(self, text="Cryptographically secure passwords", bg=BG, fg=MUTED,
                 font=("Segoe UI", 12)).pack()

        out = tk.Frame(self, bg=CARD, padx=20, pady=16)
        out.pack(fill="x", padx=24, pady=18)

        tk.Entry(out, textvariable=self.pwd_var, bg=SURFACE, fg=GOOD,
                 insertbackground=GOOD, font=("Consolas", 16, "bold"), relief="flat",
                 justify="center").pack(fill="x", ipady=10, pady=(0, 8))

        self.strength_lbl = tk.Label(out, text="", bg=CARD, font=("Segoe UI", 12, "bold"))
        self.strength_lbl.pack()

        btn_row = tk.Frame(out, bg=CARD)
        btn_row.pack(pady=(10, 0))
        tk.Button(btn_row, text="Generate", bg=ACCENT, fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self.generate).pack(side="left", padx=4)
        tk.Button(btn_row, text="Copy", bg=GOOD, fg=BG, font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self.copy).pack(side="left", padx=4)
        tk.Button(btn_row, text="Save", bg=SURFACE, fg=TEXT, font=("Segoe UI", 12),
                  relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self.save).pack(side="left", padx=4)

        cfg = tk.LabelFrame(self, text=" Settings ", bg=BG, fg=MUTED, font=("Segoe UI", 12),
                             relief="flat", padx=20, pady=12)
        cfg.pack(fill="x", padx=24)

        len_row = tk.Frame(cfg, bg=BG)
        len_row.pack(fill="x", pady=(0, 10))
        tk.Label(len_row, text="Length:", bg=BG, fg=TEXT, font=("Segoe UI", 12)).pack(side="left")
        self.len_disp = tk.Label(len_row, text="16", bg=BG, fg=GOOD,
                                  font=("Segoe UI", 14, "bold"), width=3)
        self.len_disp.pack(side="right")

        tk.Scale(cfg, from_=6, to=64, orient="horizontal", variable=self.length_var,
                 bg=BG, fg=TEXT, troughcolor=SURFACE, activebackground=ACCENT,
                 highlightthickness=0, showvalue=False,
                 command=lambda v: (self.len_disp.config(text=v), self.generate())
                 ).pack(fill="x")

        tk.Label(cfg, text="Include:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12)).pack(anchor="w", pady=(8, 4))
        chk_row = tk.Frame(cfg, bg=BG)
        chk_row.pack(fill="x")
        for key, label in {"uppercase": "A-Z", "lowercase": "a-z",
                           "digits": "0-9", "symbols": "!@#…"}.items():
            tk.Checkbutton(chk_row, text=label, variable=self.use[key], bg=BG, fg=TEXT,
                           selectcolor=CARD, activebackground=BG, font=("Segoe UI", 12),
                           cursor="hand2", command=self.generate).pack(side="left", padx=8)

        exclude_row = tk.Frame(cfg, bg=BG)
        exclude_row.pack(fill="x", pady=(8, 0))
        tk.Label(exclude_row, text="Exclude chars:", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12)).pack(side="left")
        tk.Entry(exclude_row, textvariable=self.exclude_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, font=("Consolas", 12), width=16,
                 relief="flat").pack(side="left", padx=8, ipady=4)
        tk.Button(exclude_row, text="Apply", bg=SURFACE, fg=GOOD, font=("Segoe UI", 11),
                  relief="flat", padx=6, cursor="hand2", command=self.generate).pack(side="left")

        hist_frame = tk.LabelFrame(self, text=" Recent Passwords ", bg=BG, fg=MUTED,
                                    font=("Segoe UI", 12), relief="flat", padx=20, pady=8)
        hist_frame.pack(fill="both", expand=True, padx=24, pady=12)

        self.hist_box = tk.Text(hist_frame, bg=SURFACE, fg=MUTED, font=("Consolas", 11),
                                 relief="flat", state="disabled", height=6)
        self.hist_box.pack(fill="both", expand=True)
        self._refresh_history()

    def generate(self):
        try:
            pwd = generate_password(self.length_var.get(),
                                     {k: v.get() for k, v in self.use.items()},
                                     self.exclude_var.get())
            self.pwd_var.set(pwd)
            label, color = strength(pwd)
            self.strength_lbl.config(text=f"Strength: {label}", fg=color)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def copy(self):
        pwd = self.pwd_var.get()
        if not pwd:
            return
        try:
            pyperclip.copy(pwd)
        except Exception:
            self.clipboard_clear()
            self.clipboard_append(pwd)
        messagebox.showinfo("Copied", "Password copied to clipboard!")

    def save(self):
        pwd = self.pwd_var.get()
        if pwd:
            save_to_history(pwd)
            self._refresh_history()
            messagebox.showinfo("Saved", "Password saved to history.")

    def _refresh_history(self):
        self.hist_box.config(state="normal")
        self.hist_box.delete("1.0", "end")
        for entry in load_history()[:8]:
            self.hist_box.insert("end", f"{entry['time']}  {entry['password']}\n")
        self.hist_box.config(state="disabled")


if __name__ == "__main__":
    PasswordApp().mainloop()
