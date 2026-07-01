"""Thumbnail and on-the-fly rendition generation.

Images get a real downscaled thumbnail. Everything else gets a tasteful
generated placeholder card (media-type glyph) so the asset grid stays
visually consistent without shelling out to ffmpeg/ghostscript. Renditions
are produced on demand and cached in the content-addressable thumb store.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import storage

THUMB_MAX = 512        # longest edge for grid thumbnails
PREVIEW_MAX = 1600     # longest edge for the detail-view preview

# Two-tone palette mirrored from the web UI so placeholders match the app.
_BASE = (24, 28, 38)
_ACCENT = (94, 132, 247)
_GLYPH = {
    "video": "▶",
    "audio": "♪",
    "document": "≡",
    "other": "◆",
}


def _placeholder(media_type: str, label: str) -> bytes:
    img = Image.new("RGB", (THUMB_MAX, THUMB_MAX), _BASE)
    draw = ImageDraw.Draw(img)
    glyph = _GLYPH.get(media_type, _GLYPH["other"])
    try:
        font = ImageFont.truetype("arial.ttf", 180)
        small = ImageFont.truetype("arial.ttf", 34)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((THUMB_MAX / 2, THUMB_MAX / 2 - 30), glyph, font=font, fill=_ACCENT, anchor="mm")
    draw.text((THUMB_MAX / 2, THUMB_MAX - 70), label[:22], font=small, fill=(150, 160, 180), anchor="mm")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def make_thumbnail(blob: Path, media_type: str, ext: str, max_edge: int = THUMB_MAX) -> bytes:
    if media_type == "image":
        try:
            with Image.open(blob) as img:
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGB") if img.mode not in ("RGB", "L") else img
                img.thumbnail((max_edge, max_edge), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=82)
                return buf.getvalue()
        except Exception:
            return _placeholder("other", ext.upper())
    return _placeholder(media_type, ext.upper())


def ensure_thumbnail(sha: str, blob_key: str, media_type: str, ext: str) -> str:
    """Generate (if needed) and cache a grid thumbnail. Returns its key."""
    key = f"{sha[:2]}/{sha[2:4]}/{sha}_thumb.jpg"
    out = storage.thumb_path(key)
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        data = make_thumbnail(storage.blob_path(blob_key), media_type, ext)
        out.write_bytes(data)
    return key


def rendition(sha: str, blob_key: str, media_type: str, ext: str, max_edge: int) -> Optional[bytes]:
    """On-the-fly resized rendition (cached). Images only."""
    if media_type != "image":
        return None
    key = f"{sha[:2]}/{sha[2:4]}/{sha}_{max_edge}.jpg"
    out = storage.thumb_path(key)
    if out.exists():
        return out.read_bytes()
    data = make_thumbnail(storage.blob_path(blob_key), media_type, ext, max_edge=max_edge)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return data
