"""
Pixel Pet Planner (PPP) - By Shane Silva, UniKey: SSIL0126, SID:550825698

Run with:
    python3 main.py

Then open:
    http://127.0.0.1:8000
"""

## These Imports have been identified with the use of AI.
from __future__ import annotations

import argparse
import json
import mimetypes
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "pixel_pet_tasks.json"
DAILY_GOAL = 5


# Multi-dimensional list:
# Rows represent the urgency, columns represent completed task count from 0-5.
# The app indexes this grid to choose the cat's mood from two dimensions at once.
CAT_MOOD_GRID = [
    [
        {
            "name": "Very Hungry",
            "pose": "hungry",
            "energy": 12,
            "message": "The cat is tapping the empty bowl. Complete a task to feed it.",
        },
        {
            "name": "Still Hungry",
            "pose": "hungry",
            "energy": 28,
            "message": "One snack helped, but the cat is still waiting for more.",
        },
        {
            "name": "Peckish",
            "pose": "sleepy",
            "energy": 42,
            "message": "The cat is calmer, but the bowl is not full yet.",
        },
        {
            "name": "Hopeful",
            "pose": "happy",
            "energy": 58,
            "message": "The cat can see the day improving.",
        },
        {
            "name": "Almost Full",
            "pose": "happy",
            "energy": 76,
            "message": "One more completed task will make the cat's day.",
        },
        {
            "name": "Full",
            "pose": "full",
            "energy": 100,
            "message": "Five tasks done. The cat is fed, full, and proud.",
        },
    ],
    [
        {
            "name": "Curious",
            "pose": "idle",
            "energy": 25,
            "message": "The cat is watching the list and waiting for the first snack.",
        },
        {
            "name": "Nibbling",
            "pose": "happy",
            "energy": 40,
            "message": "The cat enjoyed that first task.",
        },
        {
            "name": "Perky",
            "pose": "happy",
            "energy": 55,
            "message": "The cat is pacing around happily.",
        },
        {
            "name": "Bright",
            "pose": "happy",
            "energy": 70,
            "message": "The cat has a bright little sparkle today.",
        },
        {
            "name": "Nearly Fed",
            "pose": "happy",
            "energy": 85,
            "message": "The bowl is nearly full.",
        },
        {
            "name": "Full",
            "pose": "full",
            "energy": 100,
            "message": "Five tasks done. The cat is fed, full, and proud.",
        },
    ],
    [
        {
            "name": "Ready",
            "pose": "idle",
            "energy": 35,
            "message": "The cat is ready to help you start.",
        },
        {
            "name": "Happy",
            "pose": "happy",
            "energy": 48,
            "message": "The cat got a fresh snack from that task.",
        },
        {
            "name": "Playful",
            "pose": "happy",
            "energy": 64,
            "message": "Two tasks done. The cat is feeling playful.",
        },
        {
            "name": "Cheerful",
            "pose": "happy",
            "energy": 78,
            "message": "Three tasks done. The cat is cheering you on.",
        },
        {
            "name": "Excited",
            "pose": "happy",
            "energy": 92,
            "message": "Four tasks done. The cat is almost completely full.",
        },
        {
            "name": "Full",
            "pose": "full",
            "energy": 100,
            "message": "Five tasks done. The cat is fed, full, and proud.",
        },
    ],
]

## Returning todays date in ISO format
def today_string():
    return datetime.now().date().isoformat()


def now_string():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

## Reading saved app data
def read_data():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        return {"users": {}}

    with DATA_FILE.open("r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {"users": {}}

## Writing app data into JSON using a temp file swap
def write_data(data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    temp_file.replace(DATA_FILE)

## Converts the name into a simple username
def clean_username(raw_name: str):
    cleaned = "".join(
        char.lower() for char in raw_name.strip() if char.isalnum() or char in ("-", "_")
    )
    return cleaned[:24] or "guest"


## Find or create the user profile
def get_or_create_user(data: dict, display_name: str):
    display_name = display_name.strip() or "Guest"
    username = clean_username(display_name)
    users = data.setdefault("users", {})
    if username not in users:
        users[username] = {
            "display_name": display_name[:32],
            "created_at": now_string(),
            "last_login": now_string(),
            "tasks": [],
        }
    else:
        users[username]["display_name"] = display_name[:32]
        users[username]["last_login"] = now_string()
    return username, users[username]


## I recursively collect the tasks for the day, each call solves the same problem for the rest of the list
## until the base case reaches the end.
def recursive_tasks_for_day(tasks: list[dict], target_day: str, index: int = 0):
    if index >= len(tasks):
        return []

    current_task = tasks[index]
    rest_of_list = recursive_tasks_for_day(tasks, target_day, index + 1)
    if current_task.get("date") == target_day:
        return [current_task] + rest_of_list
    return rest_of_list

## Counting completed tasks for todays cat feeding goal
def recursive_count_completed(tasks: list[dict], index: int = 0):
    if index >= len(tasks):
        return 0

    current_value = 1 if tasks[index].get("completed") else 0
    return current_value + recursive_count_completed(tasks, index + 1)

## Counting unfinished tasks
def count_pending(tasks: list[dict]) -> int:
    pending = 0
    for task in tasks:
        if not task.get("completed"):
            pending += 1
    return pending

## Hours since recently completed task
def hours_since_last_completion(tasks: list[dict]):
    completed_times = []
    for task in tasks:
        completed_at = task.get("completed_at")
        if completed_at:
            try:
                completed_times.append(datetime.fromisoformat(completed_at))
            except ValueError:
                pass

    if not completed_times:
        return None

    latest = max(completed_times)
    return (datetime.now(timezone.utc) - latest).total_seconds() / 3600

## Flow control to choose the row od the cat mood grid
def cat_urgency_row(completed_count: int, pending_count: int, quiet_hours: float | None):
    if completed_count >= DAILY_GOAL:
        return 2
    if pending_count >= DAILY_GOAL and completed_count < 2:
        return 0
    if quiet_hours is None and pending_count > 0:
        return 0
    if quiet_hours is not None and quiet_hours >= 6:
        return 0
    if completed_count > 0:
        return 2
    return 1

## Create the cats mood from the completed tasks, pending tasks and time
def build_cat_state(todays_tasks: list[dict]):
    completed_count = recursive_count_completed(todays_tasks)
    pending_count = count_pending(todays_tasks)
    quiet_hours = hours_since_last_completion(todays_tasks)

    column = min(completed_count, DAILY_GOAL)
    row = cat_urgency_row(completed_count, pending_count, quiet_hours)
    mood = dict(CAT_MOOD_GRID[row][column])
    mood["completed_today"] = completed_count
    mood["pending_today"] = pending_count
    mood["daily_goal"] = DAILY_GOAL
    mood["quiet_hours"] = quiet_hours
    mood["bowl_percent"] = min(100, int((completed_count / DAILY_GOAL) * 100))
    return mood

## Return the state to the frontend
def build_state(username: str, user: dict):
    todays_tasks = recursive_tasks_for_day(user.get("tasks", []), today_string())
    todays_tasks.sort(key=lambda task: task.get("created_at", ""))
    return {
        "username": username,
        "display_name": user.get("display_name", "Guest"),
        "today": today_string(),
        "daily_goal": DAILY_GOAL,
        "tasks": todays_tasks,
        "cat": build_cat_state(todays_tasks),
    }

## Adding a task for todays list
def add_task(data: dict, username: str, text: str):
    user = data["users"][username]
    new_task = {
        "id": uuid.uuid4().hex[:10],
        "text": text.strip()[:90],
        "date": today_string(),
        "created_at": now_string(),
        "completed": False,
        "completed_at": None,
    }
    user.setdefault("tasks", []).append(new_task)
    return new_task

## Find a task by ID
def find_task(tasks: list[dict], task_id: str):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


## THIS HHTP REQUEST HANDLER WAS CREATED WITH AI ASSISTANCE (since i am not knowledgable about this implementation)

class PixelPetHandler(BaseHTTPRequestHandler):
    """HTTP request handler for static files and JSON API routes."""

    server_version = "PixelPetPlanner/1.0"

    def log_message(self, format: str, *args: object):
        """Keep terminal output tidy during class demos."""
        return

    def send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.handle_state(parsed.query)
        else:
            self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        routes = {
            "/api/login": self.handle_login,
            "/api/tasks": self.handle_add_task,
            "/api/tasks/toggle": self.handle_toggle_task,
            "/api/tasks/delete": self.handle_delete_task,
            "/api/tasks/clear-completed": self.handle_clear_completed,
        }
        handler = routes.get(parsed.path)
        if handler is None:
            self.send_json({"error": "Unknown route."}, status=404)
            return
        handler()

    def serve_static(self, request_path: str):
        if request_path == "/":
            request_path = "/index.html"

        static_file = (STATIC_DIR / request_path.lstrip("/")).resolve()
        try:
            static_file.relative_to(STATIC_DIR.resolve())
        except ValueError:
            self.send_error(404)
            return

        if not static_file.exists() or not static_file.is_file():
            self.send_error(404)
            return

        content_type = mimetypes.guess_type(static_file.name)[0] or "application/octet-stream"
        body = static_file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_state(self, query: str):
        params = parse_qs(query)
        username = clean_username(params.get("user", ["guest"])[0])
        data = read_data()
        users = data.setdefault("users", {})
        if username not in users:
            username, user = get_or_create_user(data, username)
            write_data(data)
        else:
            user = users[username]
        self.send_json(build_state(username, user))

    def handle_login(self):
        payload = self.read_json_body()
        data = read_data()
        username, user = get_or_create_user(data, payload.get("display_name", "Guest"))
        write_data(data)
        self.send_json(build_state(username, user))

    def handle_add_task(self):
        payload = self.read_json_body()
        username = clean_username(payload.get("user", "guest"))
        text = payload.get("text", "").strip()
        if not text:
            self.send_json({"error": "Task text is required."}, status=400)
            return

        data = read_data()
        users = data.setdefault("users", {})
        if username not in users:
            username, user = get_or_create_user(data, username)
        else:
            user = users[username]

        add_task(data, username, text)
        write_data(data)
        self.send_json(build_state(username, user), status=201)

    def handle_toggle_task(self):
        payload = self.read_json_body()
        username = clean_username(payload.get("user", "guest"))
        task_id = payload.get("task_id", "")
        data = read_data()
        user = data.get("users", {}).get(username)
        if user is None:
            self.send_json({"error": "User not found."}, status=404)
            return

        task = find_task(user.get("tasks", []), task_id)
        if task is None:
            self.send_json({"error": "Task not found."}, status=404)
            return

        task["completed"] = not task.get("completed", False)
        task["completed_at"] = now_string() if task["completed"] else None
        write_data(data)
        self.send_json(build_state(username, user))

    def handle_delete_task(self):
        payload = self.read_json_body()
        username = clean_username(payload.get("user", "guest"))
        task_id = payload.get("task_id", "")
        data = read_data()
        user = data.get("users", {}).get(username)
        if user is None:
            self.send_json({"error": "User not found."}, status=404)
            return

        user["tasks"] = [task for task in user.get("tasks", []) if task.get("id") != task_id]
        write_data(data)
        self.send_json(build_state(username, user))

    def handle_clear_completed(self):
        payload = self.read_json_body()
        username = clean_username(payload.get("user", "guest"))
        data = read_data()
        user = data.get("users", {}).get(username)
        if user is None:
            self.send_json({"error": "User not found."}, status=404)
            return

        today = today_string()
        user["tasks"] = [
            task
            for task in user.get("tasks", [])
            if task.get("date") != today or not task.get("completed")
        ]
        write_data(data)
        self.send_json(build_state(username, user))


def run_server(host: str, port: int):
    server = ThreadingHTTPServer((host, port), PixelPetHandler)
    print(f"Pixel Pet Planner running at http://{host}:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Pixel Pet Planner app.")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind.")
    parser.add_argument("--port", default=8000, type=int, help="Port to run on.")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_server(arguments.host, arguments.port)
