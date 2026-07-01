"""Authentication, password hashing, and role-based access control.

Tokens are stateless HMAC-signed payloads (a minimal JWT-style scheme)
built entirely on the standard library, so there is no cryptography
dependency to install. Passwords are hashed with scrypt.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional

from .config import config
from .db import get_conn

# Role hierarchy: each role implies every capability of the ones after it.
ROLES = ["admin", "editor", "contributor", "viewer"]
_RANK = {r: i for i, r in enumerate(ROLES)}


def role_at_least(role: str, minimum: str) -> bool:
    return _RANK.get(role, 99) <= _RANK.get(minimum, 99)


# ----------------------------------------------------------------------------
# Password hashing (scrypt, stdlib)
# ----------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, hash_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


# ----------------------------------------------------------------------------
# Token signing
# ----------------------------------------------------------------------------
def _secret() -> bytes:
    if config.secret_key:
        return config.secret_key.encode()
    # Persist a generated secret so tokens survive restarts in dev.
    conn = get_conn()
    row = conn.execute("SELECT value FROM schema_meta WHERE key = 'secret_key'").fetchone()
    if row:
        return row["value"].encode()
    generated = secrets.token_hex(32)
    conn.execute(
        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('secret_key', ?)",
        (generated,),
    )
    conn.commit()
    return generated.encode()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def make_token(user_id: int, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": int(time.time()) + config.token_ttl_hours * 3600,
    }
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(_secret(), body.encode(), hashlib.sha256).digest()
    return f"{body}.{_b64(sig)}"


def verify_token(token: str) -> Optional[dict]:
    try:
        body, sig = token.split(".")
        expected = hmac.new(_secret(), body.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_unb64(sig), expected):
            return None
        payload = json.loads(_unb64(body))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def authenticate(username: str, password: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
    ).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return dict(row)
    return None
