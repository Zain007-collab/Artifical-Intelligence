# Weather App

Shows current weather and a 5-day forecast for any city, using the OpenWeatherMap API.

## What it does
- Current temperature, "feels like", humidity, wind, visibility
- 5-day forecast with daily high/low
- Switch between °C and °F
- Remembers your last city and API key between sessions

## How to run
1. Get a free API key from https://openweathermap.org/api
2. Install dependencies and run:
```bash
pip install -r requirements.txt
python main.py
```
3. Paste your API key into the app and hit "Save Key"
4. Search any city

## What I practiced
- Calling a real REST API with `requests` and handling errors (bad key, city not found, no internet)
- Parsing the 3-hour forecast data down into one entry per day
- Saving small bits of config (API key, last city) to a JSON file
- Building a UI that updates itself after an API call comes back

## Project structure
```
07_Weather_App/
├── main.py
├── config.json      ← auto-created (stores API key + last city)
├── README.md
└── requirements.txt
```
