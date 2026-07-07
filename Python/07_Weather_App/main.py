"""Weather App — Tkinter GUI backed by the OpenWeatherMap REST API."""

import json
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

import requests

CONFIG_FILE = Path(__file__).parent / "config.json"
BASE_URL = "https://api.openweathermap.org/data/2.5"

BG, CARD, SURFACE = "#1a1b26", "#20222f", "#292e42"
ACCENT, GOOD = "#7dcfff", "#9ece6a"
TEXT, MUTED = "#c0caf5", "#565f89"

WEATHER_ICONS = {
    "Clear": "☀", "Clouds": "☁", "Rain": "🌧", "Drizzle": "🌦",
    "Thunderstorm": "⛈", "Snow": "❄", "Mist": "🌫", "Fog": "🌫",
    "Haze": "🌫", "Smoke": "🌫", "Dust": "🌪", "Sand": "🌪",
    "Wind": "💨", "Tornado": "🌪",
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {"api_key": "", "unit": "metric", "last_city": "London"}


def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def get_weather(city: str, api_key: str, unit: str = "metric") -> dict:
    """Fetch current conditions + 5-day forecast from OpenWeatherMap."""
    params = {"q": city, "appid": api_key, "units": unit}
    current = requests.get(f"{BASE_URL}/weather", params=params, timeout=8)
    current.raise_for_status()
    forecast = requests.get(f"{BASE_URL}/forecast", params=params, timeout=8)
    forecast.raise_for_status()
    return {"current": current.json(), "forecast": forecast.json()}


def parse_forecast(forecast: dict) -> list[dict]:
    """Collapse the 3-hourly forecast into one min/max entry per day."""
    days: dict[str, dict] = {}
    for item in forecast["list"]:
        day = item["dt_txt"][:10]
        temp_min, temp_max = item["main"]["temp_min"], item["main"]["temp_max"]
        if day not in days:
            days[day] = {"date": day, "desc": item["weather"][0]["main"],
                         "min": temp_min, "max": temp_max}
        else:
            days[day]["min"] = min(days[day]["min"], temp_min)
            days[day]["max"] = max(days[day]["max"], temp_max)
    return list(days.values())[1:6]


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("560x720")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.cfg = load_config()
        self.city = tk.StringVar(value=self.cfg.get("last_city", ""))
        self.unit = tk.StringVar(value=self.cfg.get("unit", "metric"))

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg=CARD, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Weather App", bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=20)

        unit_frame = tk.Frame(header, bg=CARD)
        unit_frame.pack(side="right", padx=16)
        for val, label in [("metric", "°C"), ("imperial", "°F")]:
            tk.Radiobutton(unit_frame, text=label, variable=self.unit, value=val, bg=CARD,
                           fg=TEXT, selectcolor=SURFACE, activebackground=CARD,
                           font=("Segoe UI", 12), command=self.search).pack(side="left", padx=4)

        search_bar = tk.Frame(self, bg=BG, pady=12)
        search_bar.pack(fill="x", padx=20)
        entry = tk.Entry(search_bar, textvariable=self.city, bg=SURFACE, fg=TEXT,
                          insertbackground=TEXT, font=("Segoe UI", 14), relief="flat", width=28)
        entry.pack(side="left", padx=(0, 8), ipady=8)
        entry.bind("<Return>", lambda e: self.search())
        tk.Button(search_bar, text="Search", bg=ACCENT, fg=BG, font=("Segoe UI", 12, "bold"),
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  command=self.search).pack(side="left")

        key_row = tk.Frame(self, bg=BG)
        key_row.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(key_row, text="API Key:", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
        self.key_var = tk.StringVar(value=self.cfg.get("api_key", ""))
        tk.Entry(key_row, textvariable=self.key_var, bg=SURFACE, fg=MUTED,
                 insertbackground=MUTED, font=("Consolas", 10), relief="flat", width=36,
                 show="•").pack(side="left", padx=6, ipady=3)
        tk.Button(key_row, text="Save Key", bg=SURFACE, fg=ACCENT, font=("Segoe UI", 10),
                  relief="flat", padx=6, pady=2, cursor="hand2",
                  command=self.save_key).pack(side="left")

        self.current_card = tk.Frame(self, bg=CARD, padx=20, pady=16)
        self.current_card.pack(fill="x", padx=20, pady=6)

        self.icon_lbl = tk.Label(self.current_card, bg=CARD, font=("Segoe UI", 48))
        self.icon_lbl.pack()
        self.temp_lbl = tk.Label(self.current_card, bg=CARD, fg=TEXT, font=("Segoe UI", 40, "bold"))
        self.temp_lbl.pack()
        self.desc_lbl = tk.Label(self.current_card, bg=CARD, fg=MUTED, font=("Segoe UI", 14))
        self.desc_lbl.pack()
        self.city_lbl = tk.Label(self.current_card, bg=CARD, fg=ACCENT, font=("Segoe UI", 16, "bold"))
        self.city_lbl.pack(pady=(4, 0))

        self.details = tk.Frame(self.current_card, bg=CARD)
        self.details.pack(pady=8)

        tk.Label(self, text="5-Day Forecast", bg=BG, fg=MUTED,
                 font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.forecast_frame = tk.Frame(self, bg=BG)
        self.forecast_frame.pack(fill="x", padx=20, pady=(4, 12))

        self.updated_lbl = tk.Label(self, bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.updated_lbl.pack(pady=4)

        if self.city.get() and self.cfg.get("api_key"):
            self.after(500, self.search)

    def save_key(self):
        self.cfg["api_key"] = self.key_var.get().strip()
        save_config(self.cfg)
        messagebox.showinfo("Saved", "API key saved.")

    def search(self):
        city = self.city.get().strip()
        api_key = self.key_var.get().strip() or self.cfg.get("api_key", "")

        if not city:
            messagebox.showwarning("Input", "Enter a city name.")
            return
        if not api_key:
            messagebox.showwarning("API Key",
                "Enter your OpenWeatherMap API key.\n"
                "Get a free key at https://openweathermap.org/api")
            return

        self.city_lbl.config(text="Loading…")
        self.update()

        try:
            data = get_weather(city, api_key, self.unit.get())
            self._show_current(data["current"])
            self._show_forecast(data["forecast"])
            self.cfg.update(last_city=city, api_key=api_key, unit=self.unit.get())
            save_config(self.cfg)
            self.updated_lbl.config(text=f"Updated {datetime.now().strftime('%H:%M:%S')}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                messagebox.showerror("API Error", "Invalid API key.")
            elif e.response.status_code == 404:
                messagebox.showerror("Not Found", f"City '{city}' not found.")
            else:
                messagebox.showerror("Error", str(e))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Network", "No internet connection.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_current(self, data: dict):
        unit_sym = "°C" if self.unit.get() == "metric" else "°F"
        wind_unit = "m/s" if self.unit.get() == "metric" else "mph"
        main = data["weather"][0]["main"]

        self.icon_lbl.config(text=WEATHER_ICONS.get(main, "🌡"))
        self.temp_lbl.config(text=f"{round(data['main']['temp'])}{unit_sym}")
        self.desc_lbl.config(text=data["weather"][0]["description"].title())
        self.city_lbl.config(text=f"{data['name']}, {data['sys']['country']}")

        for w in self.details.winfo_children():
            w.destroy()

        details = [
            ("Feels Like", f"{round(data['main']['feels_like'])}{unit_sym}"),
            ("Humidity", f"{data['main']['humidity']}%"),
            ("Wind", f"{data['wind']['speed']} {wind_unit}"),
            ("Visibility", f"{data.get('visibility', 0) // 1000} km"),
        ]
        for i, (label, value) in enumerate(details):
            row, col = i // 2, (i % 2) * 2
            tk.Label(self.details, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 11)
                     ).grid(row=row, column=col, padx=12, pady=2, sticky="w")
            tk.Label(self.details, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")
                     ).grid(row=row, column=col + 1, padx=(0, 20), pady=2, sticky="w")

    def _show_forecast(self, forecast: dict):
        for w in self.forecast_frame.winfo_children():
            w.destroy()

        unit_sym = "°C" if self.unit.get() == "metric" else "°F"
        for day in parse_forecast(forecast):
            card = tk.Frame(self.forecast_frame, bg=CARD, padx=10, pady=8)
            card.pack(side="left", expand=True, fill="x", padx=4)

            name = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%a")
            tk.Label(card, text=name, bg=CARD, fg=MUTED, font=("Segoe UI", 11)).pack()
            tk.Label(card, text=WEATHER_ICONS.get(day["desc"], "🌡"), bg=CARD,
                     font=("Segoe UI", 22)).pack()
            tk.Label(card, text=f"{round(day['max'])}{unit_sym}", bg=CARD, fg=TEXT,
                     font=("Segoe UI", 12, "bold")).pack()
            tk.Label(card, text=f"{round(day['min'])}{unit_sym}", bg=CARD, fg=MUTED,
                     font=("Segoe UI", 11)).pack()


if __name__ == "__main__":
    WeatherApp().mainloop()
