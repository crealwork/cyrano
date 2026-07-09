"""Dedup store — don't brief the same (date, event, person) twice.

A morning routine may fire more than once (retries, manual re-runs, overlapping
cron windows). Research is expensive (many page fetches), so before spending it
we check a small JSON ledger. Entries older than the dedup window are ignored,
so a recurring weekly meeting with the same person still gets re-briefed next
week.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def _path(cfg: dict[str, Any]) -> Path:
    return Path(cfg["dedup"]["state_file"])


def _load(path: Path) -> dict[str, float]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def key(date: str, event_id: str, email: str) -> str:
    return f"{date}:{event_id}:{email.strip().lower()}"


def is_briefed(cfg: dict[str, Any], date: str, event_id: str, email: str) -> bool:
    window_s = float(cfg["dedup"].get("window_hours", 20)) * 3600
    ledger = _load(_path(cfg))
    ts = ledger.get(key(date, event_id, email))
    if ts is None:
        return False
    return (time.time() - ts) < window_s


def mark(cfg: dict[str, Any], date: str, event_id: str, email: str) -> None:
    path = _path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    ledger = _load(path)
    ledger[key(date, event_id, email)] = time.time()
    # prune anything older than 30 days so the file can't grow forever
    cutoff = time.time() - 30 * 86400
    ledger = {k: v for k, v in ledger.items() if v >= cutoff}
    path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")


def clear(cfg: dict[str, Any]) -> None:
    path = _path(cfg)
    if path.exists():
        path.unlink()
