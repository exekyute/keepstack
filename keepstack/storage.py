"""Content-addressable blob storage.

Every byte stream is stored once, keyed by its SHA-256 digest. Two uploads
of the same file collapse to a single blob automatically (deduplication),
and the digest doubles as a fixity/integrity check for digital preservation.

Layout:  blobs/<aa>/<bb>/<full-sha256>

The first four hex characters fan out into nested directories so a single
folder never holds millions of files.
"""
from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import BinaryIO

from .config import config

CHUNK = 1024 * 1024  # 1 MiB


def _key_to_path(base: Path, sha: str, ext: str = "") -> Path:
    name = sha + (("." + ext) if ext else "")
    return base / sha[:2] / sha[2:4] / name


def storage_key(sha: str, ext: str = "") -> str:
    """Relative key recorded in the database."""
    name = sha + (("." + ext) if ext else "")
    return f"{sha[:2]}/{sha[2:4]}/{name}"


def blob_path(key: str) -> Path:
    return config.blob_dir / key


def thumb_path(key: str) -> Path:
    return config.thumb_dir / key


def store_stream(src: BinaryIO, ext: str = "") -> tuple[str, str, int]:
    """Stream ``src`` to a temp file, hash it, then move into place.

    Returns ``(sha256, storage_key, size)``. If a blob with the same hash
    already exists the temp file is discarded and the existing blob reused.
    """
    config.ensure_dirs()
    tmp = config.cache_dir / f"upload-{os.getpid()}-{id(src)}.part"
    h = hashlib.sha256()
    size = 0
    with open(tmp, "wb") as out:
        while True:
            chunk = src.read(CHUNK)
            if not chunk:
                break
            out.write(chunk)
            h.update(chunk)
            size += len(chunk)
    sha = h.hexdigest()
    key = storage_key(sha, ext)
    dest = blob_path(key)
    if dest.exists():
        tmp.unlink(missing_ok=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp), str(dest))
    return sha, key, size


def store_bytes(data: bytes, ext: str = "") -> tuple[str, str, int]:
    sha = hashlib.sha256(data).hexdigest()
    key = storage_key(sha, ext)
    dest = blob_path(key)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return sha, key, len(data)


def verify_fixity(key: str, expected_sha: str) -> bool:
    """Re-hash a stored blob and compare against the recorded digest."""
    p = blob_path(key)
    if not p.exists():
        return False
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest() == expected_sha


def delete_blob_if_orphan(key: str, still_referenced: bool) -> None:
    if not still_referenced:
        blob_path(key).unlink(missing_ok=True)


def _blob_keys() -> list[str]:
    if not config.blob_dir.exists():
        return []
    return [
        p.relative_to(config.blob_dir).as_posix()
        for p in config.blob_dir.rglob("*")
        if p.is_file()
    ]


def _referenced_blob_keys() -> set[str]:
    from .db import get_conn

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT storage_key FROM assets
        WHERE status != 'deleted' AND storage_key IS NOT NULL
        UNION
        SELECT v.storage_key FROM asset_versions v
        JOIN assets a ON a.id = v.asset_id
        WHERE a.status != 'deleted' AND v.storage_key IS NOT NULL
        """
    ).fetchall()
    return {r["storage_key"] for r in rows}


def _prune_empty_dirs(path: Path) -> None:
    while path != config.blob_dir and config.blob_dir in path.parents:
        try:
            path.rmdir()
        except OSError:
            return
        path = path.parent


def collect_orphan_blobs(*, dry_run: bool = False) -> dict:
    """Remove blob files not referenced by active assets or their versions."""
    config.ensure_dirs()
    referenced = _referenced_blob_keys()
    orphaned: list[dict] = []
    total_bytes = 0

    for key in _blob_keys():
        if key in referenced:
            continue
        path = blob_path(key)
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            continue
        orphaned.append({"key": key, "bytes": size})
        total_bytes += size
        if not dry_run:
            path.unlink(missing_ok=True)
            _prune_empty_dirs(path.parent)

    return {
        "dry_run": dry_run,
        "orphaned": len(orphaned),
        "removed": 0 if dry_run else len(orphaned),
        "bytes": total_bytes,
        "blobs": orphaned,
    }
