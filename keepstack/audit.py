"""Tamper-evident-ish audit logging.

Every state-changing action is recorded with who, what, when, and from
where. Government and records-management deployments treat a complete,
queryable audit trail as table stakes, so Keepstack writes one for free on
every mutating endpoint.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .db import get_conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(
    action: str,
    *,
    user: Optional[dict] = None,
    target_type: Optional[str] = None,
    target_id: Optional[object] = None,
    detail: Optional[str] = None,
    ip: Optional[str] = None,
) -> None:
    conn = get_conn()
    conn.execute(
        """INSERT INTO audit_log (ts, user_id, username, action, target_type, target_id, detail, ip)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            now_iso(),
            (user or {}).get("id"),
            (user or {}).get("username"),
            action,
            target_type,
            str(target_id) if target_id is not None else None,
            detail,
            ip,
        ),
    )
    conn.commit()
