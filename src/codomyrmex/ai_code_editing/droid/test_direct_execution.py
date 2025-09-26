#!/usr/bin/env python3
"""Test script to verify direct execution works."""

from todo import TodoManager
import os

# Get the directory of this test script
script_dir = os.path.dirname(os.path.abspath(__file__))
todo_file = os.path.join(script_dir, "todo_list.txt")

print(f"Testing direct execution from: {script_dir}")
print(f"TODO file path: {todo_file}")

manager = TodoManager(todo_file)
todo_items, completed_items = manager.load()

print(f"✅ Direct execution test successful!")
print(f"📋 TODO items: {len(todo_items)}")
print(f"✅ Completed items: {len(completed_items)}")

if len(completed_items) > 0:
    print("Recent completions:")
    for item in completed_items[-3:]:  # Show last 3
        print(f"  ✅ {item.operation_id}: {item.description}")
