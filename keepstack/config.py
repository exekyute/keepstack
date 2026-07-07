"""Runtime configuration.

Everything is environment-driven with safe local defaults so a fresh
checkout runs with zero configuration. Point ``KEEPSTACK_DATA_DIR`` somewhere
persistent for real deployments.
"""
from __future__ import annotations

import os
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    def __init__(self) -> None:
        self.data_dir = Path(os.environ.get("KEEPSTACK_DATA_DIR", "data")).resolve()
        self.db_path = self.data_dir / "keepstack.db"
        self.blob_dir = self.data_dir / "blobs"          # content-addressable store
        self.thumb_dir = self.data_dir / "thumbnails"
        self.cache_dir = self.data_dir / "cache"

        # Auth
        self.secret_key = os.environ.get("KEEPSTACK_SECRET_KEY", "")
        self.token_ttl_hours = int(os.environ.get("KEEPSTACK_TOKEN_TTL_HOURS", "168"))

        # Login throttling: lock out after N failures within the window, both
        # per (username, ip) and per ip. Trusted proxies let client_ip honour
        # X-Forwarded-For; without them the direct peer address is used.
        self.login_max_attempts = int(os.environ.get("KEEPSTACK_LOGIN_MAX_ATTEMPTS", "5"))
        self.login_max_attempts_per_ip = int(os.environ.get("KEEPSTACK_LOGIN_MAX_ATTEMPTS_PER_IP", "20"))
        self.login_lockout_seconds = int(os.environ.get("KEEPSTACK_LOGIN_LOCKOUT_SECONDS", "300"))
        self.trusted_proxies = [p.strip() for p in
                                os.environ.get("KEEPSTACK_TRUSTED_PROXIES", "").split(",") if p.strip()]

        # Bootstrap admin (only used the first time the DB is created)
        self.admin_user = os.environ.get("KEEPSTACK_ADMIN_USER", "admin")
        self.admin_password = os.environ.get("KEEPSTACK_ADMIN_PASSWORD", "admin")

        # Uploads
        self.max_upload_mb = int(os.environ.get("KEEPSTACK_MAX_UPLOAD_MB", "1024"))

        # Optional OCR via the Tesseract binary (used only when installed).
        self.ocr_enabled = _env_bool("KEEPSTACK_OCR_ENABLED", True)

        # Optional AI provider. When unset, Keepstack runs fully offline with
        # deterministic local fallbacks; nothing breaks.
        self.ai_enabled = _env_bool("KEEPSTACK_AI_ENABLED", False)
        self.ai_provider = os.environ.get("KEEPSTACK_AI_PROVIDER", "local")
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.cohere_api_key = os.environ.get("COHERE_API_KEY", "")

        # Instance identity (used in OAI-PMH / IIIF base URLs)
        self.base_url = os.environ.get("KEEPSTACK_BASE_URL", "http://localhost:8000")
        self.repository_name = os.environ.get("KEEPSTACK_REPOSITORY_NAME", "Keepstack Repository")
        self.admin_email = os.environ.get("KEEPSTACK_ADMIN_EMAIL", "admin@example.org")

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.blob_dir, self.thumb_dir, self.cache_dir):
            d.mkdir(parents=True, exist_ok=True)


config = Config()
