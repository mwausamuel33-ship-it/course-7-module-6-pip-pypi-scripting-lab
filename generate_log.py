#!/usr/bin/env python3
"""
Simple CLI Task Manager and Log Generator

This script helps manage tasks and generate logs.
It can also fetch data from the internet and save it to files.

Usage:
  python generate_log.py generate-log
  python generate_log.py add-task --user alice --title "Write docs"
  python generate_log.py complete-task --user alice --id 1
  python generate_log.py list-tasks --user alice
  python generate_log.py fetch-post --id 1
"""

import argparse
import json
import os
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None


def generate_log(args):
    """Create a log file with today's date and some sample entries."""
    log_data = ["User logged in", "User updated profile", "Report exported"]
    filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
    
    with open(filename, "w") as file:
        for entry in log_data:
            file.write(f"{entry}\n")
    
    print(f"Log written to {filename}")


def add_task(args):
    """Add a new task for a user."""
    user = args.user
    title = args.title
    
    # Create data directory if it doesn't exist
    if not os.path.exists(".data"):
        os.makedirs(".data")
    
    # Load existing tasks or create empty dict
    tasks_file = ".data/tasks.json"
    if os.path.exists(tasks_file):
        with open(tasks_file, "r") as f:
            all_tasks = json.load(f)
    else:
        all_tasks = {}
    
    # Get user's tasks or create empty list
    user_tasks = all_tasks.get(user, [])
    
    # Find next task ID
    if user_tasks:
        next_id = max(task["id"] for task in user_tasks) + 1
    else:
        next_id = 1
    
    # Create new task
    new_task = {
        "id": next_id,
        "title": title,
        "completed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    user_tasks.append(new_task)
    all_tasks[user] = user_tasks
    
    # Save tasks
    with open(tasks_file, "w") as f:
        json.dump(all_tasks, f, indent=2)
    
    print(f"Task added for {user}: #{new_task['id']} - {new_task['title']}")


def complete_task(args):
    """Mark a task as completed."""
    user = args.user
    task_id = args.id
    
    tasks_file = ".data/tasks.json"
    if not os.path.exists(tasks_file):
        print(f"No tasks found for user {user}")
        return
    
    with open(tasks_file, "r") as f:
        all_tasks = json.load(f)
    
    user_tasks = all_tasks.get(user, [])
    
    # Find and complete the task
    for task in user_tasks:
        if task["id"] == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.utcnow().isoformat()
            
            # Save updated tasks
            with open(tasks_file, "w") as f:
                json.dump(all_tasks, f, indent=2)
            
            print(f"Task completed for {user}: #{task['id']} - {task['title']}")
            return
    
    print(f"No task with id {task_id} found for user {user}")


def list_tasks(args):
    """List all tasks for a user."""
    user = args.user
    
    tasks_file = ".data/tasks.json"
    if not os.path.exists(tasks_file):
        print(f"No tasks for user {user}")
        return
    
    with open(tasks_file, "r") as f:
        all_tasks = json.load(f)
    
    user_tasks = all_tasks.get(user, [])
    
    if not user_tasks:
        print(f"No tasks for user {user}")
        return
    
    for task in user_tasks:
        status = "✓" if task["completed"] else "✗"
        print(f"[{status}] #{task['id']}: {task['title']}")


def fetch_post(args):
    """Fetch a post from the internet and save it to a file."""
    if requests is None:
        print("Error: requests package not installed. Please run: pip install requests")
        return
    
    post_id = args.id
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "No title found")
            print(f"Fetched Post Title: {title}")
            
            # Save to file
            filename = f"post_{post_id}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"Post data written to {filename}")
        else:
            print(f"Failed to fetch post {post_id}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching post: {e}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Simple Task Manager and Log Generator")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate log command
    log_parser = subparsers.add_parser("generate-log", help="Create a daily log file")
    
    # Add task command
    add_parser = subparsers.add_parser("add-task", help="Add a new task")
    add_parser.add_argument("--user", required=True, help="Username")
    add_parser.add_argument("--title", required=True, help="Task title")
    
    # Complete task command
    complete_parser = subparsers.add_parser("complete-task", help="Mark a task as completed")
    complete_parser.add_argument("--user", required=True, help="Username")
    complete_parser.add_argument("--id", type=int, required=True, help="Task ID")
    
    # List tasks command
    list_parser = subparsers.add_parser("list-tasks", help="List all tasks for a user")
    list_parser.add_argument("--user", required=True, help="Username")
    
    # Fetch post command
    fetch_parser = subparsers.add_parser("fetch-post", help="Fetch a post from the internet")
    fetch_parser.add_argument("--id", type=int, default=1, help="Post ID (default: 1)")
    
    args = parser.parse_args()
    
    if args.command == "generate-log":
        generate_log(args)
    elif args.command == "add-task":
        add_task(args)
    elif args.command == "complete-task":
        complete_task(args)
    elif args.command == "list-tasks":
        list_tasks(args)
    elif args.command == "fetch-post":
        fetch_post(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
