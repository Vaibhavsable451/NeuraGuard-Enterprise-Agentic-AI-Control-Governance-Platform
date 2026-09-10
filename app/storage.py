"""
JSON-file-backed persistence layer.
Per project constraints: NO SQL / MySQL / Postgres. All durable app state
(audit logs, incidents, approvals, cost records, eval results) lives here as
append-friendly JSON documents on disk (or Azure Blob/Files in production).
"""
import json
import os
import threading
from typing import Any
from app.config import settings

_lock = threading.Lock()


def _path(collection: str) -> str:
    return os.path.join(settings.data_dir, f"{collection}.json")


def _read(collection: str) -> list[dict[str, Any]]:
    p = _path(collection)
    if not os.path.exists(p):
        return []
    with open(p, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _write(collection: str, records: list[dict[str, Any]]) -> None:
    p = _path(collection)
    with open(p, "w") as f:
        json.dump(records, f, indent=2, default=str)


def insert(collection: str, record: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        records = _read(collection)
        records.append(record)
        _write(collection, records)
    return record


def all_records(collection: str) -> list[dict[str, Any]]:
    with _lock:
        return _read(collection)


def find_one(collection: str, key: str, value: Any) -> dict[str, Any] | None:
    for r in all_records(collection):
        if r.get(key) == value:
            return r
    return None


def update_one(collection: str, key: str, value: Any, updates: dict[str, Any]) -> dict[str, Any] | None:
    with _lock:
        records = _read(collection)
        updated = None
        for r in records:
            if r.get(key) == value:
                r.update(updates)
                updated = r
                break
        if updated is not None:
            _write(collection, records)
        return updated
