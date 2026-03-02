#!/usr/bin/env python3
"""
CLI Task Manager and Log Generator

Features:
- add-task: Adds a task to a simple JSON store tied to a user
- complete-task: Marks a task complete
- generate-log: Writes a daily log file
- fetch-post: Uses requests to fetch sample data from a public API

Outputs are printed to terminal and, when relevant, written to files.

Run:
  python generate_log.py <command> [options]

Examples:
  python generate_log.py generate-log
  python generate_log.py add-task --user alice --title "Write docs"
  python generate_log.py complete-task --user alice --id 1
  python generate_log.py fetch-post --id 1
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # Delayed error if command requires it

DATA_DIR = Path(".data")
TASKS_FILE = DATA_DIR / "tasks.json"


@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    created_at: str = datetime.utcnow().isoformat()
    completed_at: Optional[str] = None


class TaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict:
        try:
            return json.loads(self.path.read_text())
        except json.JSONDecodeError:
            return {}

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2))

    def _next_id(self, user: str, tasks: List[dict]) -> int:
        return (max((t.get("id", 0) for t in tasks), default=0) + 1) if tasks else 1

    def add(self, user: str, title: str) -> Task:
        db = self._read()
        user_tasks = db.get(user, [])
        new_task = Task(id=self._next_id(user, user_tasks), title=title)
        user_tasks.append(asdict(new_task))
        db[user] = user_tasks
        self._write(db)
        return new_task

    def complete(self, user: str, task_id: int) -> Optional[Task]:
        db = self._read()
        user_tasks = db.get(user, [])
        for t in user_tasks:
            if t.get("id") == task_id:
                t["completed"] = True
                t["completed_at"] = datetime.utcnow().isoformat()
                self._write(db)
                return Task(**t)
        return None

    def list(self, user: str) -> List[Task]:
        db = self._read()
        return [Task(**t) for t in db.get(user, [])]


def cmd_generate_log(_: argparse.Namespace) -> None:
    log_data = ["User logged in", "User updated profile", "Report exported"]
    filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, "w") as file:
        for entry in log_data:
            file.write(f"{entry}\n")
    print(f"Log written to {filename}")


def cmd_add_task(ns: argparse.Namespace) -> None:
    store = TaskStore(TASKS_FILE)
    task = store.add(user=ns.user, title=ns.title)
    print(f"Task added for {ns.user}: #{task.id} - {task.title}")


def cmd_complete_task(ns: argparse.Namespace) -> None:
    store = TaskStore(TASKS_FILE)
    task = store.complete(user=ns.user, task_id=ns.id)
    if task:
        print(f"Task completed for {ns.user}: #{task.id} - {task.title}")
    else:
        print(f"No task with id {ns.id} found for user {ns.user}")


def cmd_list_tasks(ns: argparse.Namespace) -> None:
    store = TaskStore(TASKS_FILE)
    tasks = store.list(user=ns.user)
    if not tasks:
        print(f"No tasks for user {ns.user}")
        return
    for t in tasks:
        status = "✓" if t.completed else "✗"
        print(f"[{status}] #{t.id}: {t.title}")


def cmd_fetch_post(ns: argparse.Namespace) -> None:
    if requests is None:
        raise RuntimeError("The 'requests' package is required. Install with: pip install requests")
    url = f"https://jsonplaceholder.typicode.com/posts/{ns.id}"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print("Fetched Post Title:", data.get("title", "No title found"))
        # also write to file to demonstrate file I/O with external data
        out = Path(f"post_{ns.id}.json")
        out.write_text(json.dumps(data, indent=2))
        print(f"Post data written to {out}")
    else:
        print(f"Failed to fetch post {ns.id}: HTTP {resp.status_code}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CLI Task Manager and Log Generator")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate-log", help="Write a daily log file")
    g.set_defaults(func=cmd_generate_log)

    a = sub.add_parser("add-task", help="Add a task for a user")
    a.add_argument("--user", required=True)
    a.add_argument("--title", required=True)
    a.set_defaults(func=cmd_add_task)

    c = sub.add_parser("complete-task", help="Mark a user's task complete")
    c.add_argument("--user", required=True)
    c.add_argument("--id", type=int, required=True)
    c.set_defaults(func=cmd_complete_task)

    l = sub.add_parser("list-tasks", help="List tasks for a user")
    l.add_argument("--user", required=True)
    l.set_defaults(func=cmd_list_tasks)

    f = sub.add_parser("fetch-post", help="Fetch a sample post via requests and write to file")
    f.add_argument("--id", type=int, default=1)
    f.set_defaults(func=cmd_fetch_post)

    return p


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
