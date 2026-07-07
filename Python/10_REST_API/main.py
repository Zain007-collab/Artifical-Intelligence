"""REST API — FastAPI Task Manager.

Run:  uvicorn main:app --reload
Docs: http://127.0.0.1:8000/docs
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).parent / "tasks.json"

app = FastAPI(
    title="Task Manager API",
    description="A REST API for managing tasks — built with FastAPI",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    due_date: Optional[str] = None
    done: Optional[bool] = None


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[str]
    done: bool
    created_at: str
    updated_at: str


def load_tasks() -> dict[str, dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_tasks(tasks: dict):
    DATA_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def get_task_or_404(tasks: dict, task_id: str) -> dict:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return tasks[task_id]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def gen_id() -> str:
    return f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


@app.get("/", tags=["Root"])
def root():
    return {"message": "Task Manager API", "docs": "/docs", "version": "1.0.0"}


@app.get("/tasks", response_model=list[Task], tags=["Tasks"])
def list_tasks(
    done: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title/description"),
):
    """List all tasks with optional filtering."""
    tasks = list(load_tasks().values())

    if done is not None:
        tasks = [t for t in tasks if t["done"] == done]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]
    if search:
        q = search.lower()
        tasks = [t for t in tasks
                 if q in t["title"].lower() or q in (t.get("description") or "").lower()]

    return sorted(tasks, key=lambda t: t["created_at"], reverse=True)


@app.post("/tasks", response_model=Task, status_code=201, tags=["Tasks"])
def create_task(payload: TaskCreate):
    """Create a new task."""
    tasks = load_tasks()
    tid = gen_id()
    task = {
        "id": tid, "title": payload.title, "description": payload.description,
        "priority": payload.priority, "due_date": payload.due_date, "done": False,
        "created_at": now_iso(), "updated_at": now_iso(),
    }
    tasks[tid] = task
    save_tasks(tasks)
    return task


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def get_task(task_id: str):
    """Get a single task by ID."""
    return get_task_or_404(load_tasks(), task_id)


@app.patch("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(task_id: str, payload: TaskUpdate):
    """Partially update a task."""
    tasks = load_tasks()
    task = get_task_or_404(tasks, task_id)
    task.update(payload.model_dump(exclude_none=True))
    task["updated_at"] = now_iso()
    save_tasks(tasks)
    return task


@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: str):
    """Delete a task by ID."""
    tasks = load_tasks()
    get_task_or_404(tasks, task_id)
    del tasks[task_id]
    save_tasks(tasks)
    return {"deleted": task_id}


@app.patch("/tasks/{task_id}/complete", response_model=Task, tags=["Tasks"])
def complete_task(task_id: str):
    """Mark a task as done."""
    tasks = load_tasks()
    task = get_task_or_404(tasks, task_id)
    task["done"] = True
    task["updated_at"] = now_iso()
    save_tasks(tasks)
    return task


@app.get("/stats", tags=["Stats"])
def stats():
    """Summary statistics."""
    tasks = list(load_tasks().values())
    return {
        "total": len(tasks),
        "done": sum(1 for t in tasks if t["done"]),
        "active": sum(1 for t in tasks if not t["done"]),
        "by_priority": {p: sum(1 for t in tasks if t["priority"] == p)
                        for p in ("high", "medium", "low")},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
