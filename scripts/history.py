"""Ishlatilgan mavzular tarixini saqlash - takrorlanmaslik uchun."""
import json
import os

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "history.json")


def load() -> list[str]:
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def append(topic: str) -> None:
    items = load()
    items.append(topic)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
