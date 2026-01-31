"""Audit log repository (SQLite)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from src.repositories.sqlite_base import execute, init_db, query

# Audit log storage only; business logic decides when to log.


def log(actor_user_id: UUID, action: str, entity: str, entity_id: UUID, detail_json: str) -> None:
    init_db()
    execute(
        """
        INSERT INTO audit_logs (
            actor_id, action, target_type, target_id, detail, created_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?
        )
        """,
        (
            str(actor_user_id),
            action,
            entity,
            str(entity_id),
            detail_json,
            _now_iso_utc(),
        ),
    )


def list_recent(limit: int = 50) -> List[Dict[str, object]]:
    init_db()
    rows = query("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (int(limit),))
    return [dict(row) for row in rows]


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
