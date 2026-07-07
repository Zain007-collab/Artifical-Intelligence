# REST API — Task Manager

A small task manager API built with FastAPI, since I wanted to try building a backend instead of another desktop GUI.

## What it does
- Full CRUD for tasks: create, read, update, delete
- Filter tasks by status, priority, or a search keyword
- Mark a task as complete
- A `/stats` endpoint with basic counts
- Auto-generated docs at `/docs` (Swagger) and `/redoc`
- Saves everything to `tasks.json` — no real database needed

## Endpoints
| Method | Path                   | What it does              |
|--------|------------------------|---------------------------|
| GET    | `/`                    | API info                  |
| GET    | `/tasks`               | list tasks (with filters) |
| POST   | `/tasks`               | create a task             |
| GET    | `/tasks/{id}`          | get one task              |
| PATCH  | `/tasks/{id}`          | update a task             |
| DELETE | `/tasks/{id}`          | delete a task             |
| PATCH  | `/tasks/{id}/complete` | mark as done              |
| GET    | `/stats`               | summary stats             |

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Then open http://127.0.0.1:8000/docs to try it out.

## Example request
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "priority": "high"}'
```

## What I practiced
- Building an actual REST API instead of just calling one
- Request/response validation with Pydantic models
- Using proper HTTP methods and status codes
- Enabling CORS so a separate frontend could call this API

## Project structure
```
10_REST_API/
├── main.py
├── tasks.json       ← auto-created
├── README.md
└── requirements.txt
```
