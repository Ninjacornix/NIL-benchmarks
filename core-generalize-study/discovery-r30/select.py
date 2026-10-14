#!/usr/bin/env python3
"""Round 30 discovery-batch selection.

Deterministic and preregistered: from the held-out tasks (``selected == false``)
each category is sorted by ``sha256("R30:" + id)`` and the first task is taken,
or the first two when the category holds at least seven. No substitutions, so a
hard problem stays in the batch.

Run with no arguments to print the batch as JSON.
"""

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
TASKS = ROOT / "corpora/neetcode150/tasks.json"


def order_key(task_id):
    return hashlib.sha256(f"R30:{task_id}".encode()).hexdigest()


def select(tasks):
    held = [t for t in tasks if not t.get("selected")]
    categories = {}
    for task in held:
        categories.setdefault(task["category"], []).append(task)
    batch = []
    for category in sorted(categories):
        members = sorted(categories[category], key=lambda t: order_key(t["id"]))
        take = 2 if len(members) >= 7 else 1
        for task in members[:take]:
            batch.append(
                {
                    "id": task["id"],
                    "category": category,
                    "held_out_in_category": len(members),
                    "order_key": order_key(task["id"])[:16],
                }
            )
    return batch


def main():
    tasks = json.loads(TASKS.read_text())["tasks"]
    batch = select(tasks)
    print(json.dumps({"count": len(batch), "batch": batch}, indent=2))


if __name__ == "__main__":
    main()
