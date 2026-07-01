"""Technical metadata extraction.

Reads embedded EXIF, IPTC (IIM), and XMP from image files and normalises
the most useful descriptive fields (title, caption, creator, keywords,
copyright) so they can seed Keepstack's own descriptive metadata. Standards
support here is a core differentiator: archival and government workflows
live and die by IPTC / XMP fidelity.
"""
from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any, Optional

from PIL import ExifTags, Image, IptcImagePlugin

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/avif", ".avif")
mimetypes.add_type("video/webm", ".webm")

_IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp", "tif", "tiff", "bmp", "avif", "heic"}
_VIDEO_EXT = {"mp4", "mov", "webm", "mkv", "avi", "m4v"}
_AUDIO_EXT = {"mp3", "wav", "ogg", "flac", "m4a", "aac"}
_DOC_EXT = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "md", "rtf", "odt"}

# IPTC IIM record/dataset numbers -> friendly names (the common descriptive set)
_IPTC_KEYS = {
    (2, 5): "title",
    (2, 105): "headline",
    (2, 120): "caption",
    (2, 80): "creator",
    (2, 110): "credit",
    (2, 116): "copyright",
    (2, 115): "source",
    (2, 25): "keywords",
    (2, 90): "city",
    (2, 95): "state",
    (2, 101): "country",
    (2, 55): "date_created",
}


def media_type_for(ext: str, mime: Optional[str]) -> str:
    ext = (ext or "").lower().lstrip(".")
    if ext in _IMAGE_EXT or (mime or "").startswith("image/"):
        return "image"
    if ext in _VIDEO_EXT or (mime or "").startswith("video/"):
        return "video"
    if ext in _AUDIO_EXT or (mime or "").startswith("audio/"):
        return "audio"
    if ext in _DOC_EXT or (mime or "").startswith(("text/", "application/")):
        return "document"
    return "other"


def guess_mime(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", "replace")
        except Exception:
            return value.hex()
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    return str(value)


def _read_exif(img: Image.Image) -> dict:
    out: dict[str, Any] = {}
    try:
        raw = img.getexif()
    except Exception:
        return out
    for tag_id, value in raw.items():
        name = ExifTags.TAGS.get(tag_id, str(tag_id))
        out[name] = _jsonable(value)
    # GPS block, if present
    try:
        gps = raw.get_ifd(ExifTags.IFD.GPSInfo)
        if gps:
            out["GPS"] = {ExifTags.GPSTAGS.get(k, str(k)): _jsonable(v) for k, v in gps.items()}
    except Exception:
        pass
    return out


def _read_iptc(img: Image.Image) -> dict:
    out: dict[str, Any] = {}
    try:
        info = IptcImagePlugin.getiptcinfo(img)
    except Exception:
        info = None
    if not info:
        return out
    for (rec, dataset), raw in info.items():
        key = _IPTC_KEYS.get((rec, dataset))
        if not key:
            continue
        if isinstance(raw, list):
            vals = [v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v) for v in raw]
            out[key] = vals if key == "keywords" else vals[0]
        elif isinstance(raw, bytes):
            out[key] = raw.decode("utf-8", "replace")
        else:
            out[key] = str(raw)
    return out


def _read_xmp(img: Image.Image) -> dict:
    out: dict[str, Any] = {}
    xmp = img.info.get("xmp") or img.info.get("XML:com.adobe.xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", "replace")
    if isinstance(xmp, str) and xmp.strip():
        out["raw"] = xmp[:20000]
    return out


def extract(path: Path, filename: str) -> dict:
    """Return a metadata bundle for a stored blob.

    Keys: media_type, mime, width, height, duration, exif, iptc, xmp, and a
    flat ``descriptive`` dict pulled from IPTC/XMP for seeding the catalog.
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    mime = guess_mime(filename)
    mt = media_type_for(ext, mime)
    result: dict[str, Any] = {
        "media_type": mt,
        "mime": mime,
        "ext": ext,
        "width": None,
        "height": None,
        "duration": None,
        "exif": {},
        "iptc": {},
        "xmp": {},
        "descriptive": {},
    }
    if mt == "image":
        try:
            with Image.open(path) as img:
                result["width"], result["height"] = img.size
                result["exif"] = _read_exif(img)
                result["iptc"] = _read_iptc(img)
                result["xmp"] = _read_xmp(img)
        except Exception as exc:  # corrupt or unsupported image
            result["error"] = str(exc)

    # Build a descriptive layer that prefers IPTC, then EXIF, for catalog seeding.
    iptc = result["iptc"]
    exif = result["exif"]
    desc: dict[str, Any] = {}
    if iptc.get("title") or iptc.get("headline"):
        desc["title"] = iptc.get("title") or iptc.get("headline")
    if iptc.get("caption") or exif.get("ImageDescription"):
        desc["description"] = iptc.get("caption") or exif.get("ImageDescription")
    if iptc.get("creator") or exif.get("Artist"):
        desc["creator"] = iptc.get("creator") or exif.get("Artist")
    if iptc.get("copyright") or exif.get("Copyright"):
        desc["rights"] = iptc.get("copyright") or exif.get("Copyright")
    if iptc.get("keywords"):
        desc["keywords"] = iptc["keywords"]
    if iptc.get("credit"):
        desc["credit"] = iptc["credit"]
    result["descriptive"] = desc
    return result


def metadata_text(bundle: dict) -> str:
    """Flatten a metadata bundle into a searchable text blob for FTS."""
    parts: list[str] = []
    for section in ("descriptive", "iptc", "exif"):
        data = bundle.get(section) or {}
        for k, v in data.items():
            if isinstance(v, (list, tuple)):
                v = " ".join(str(x) for x in v)
            parts.append(f"{k} {v}")
    return " ".join(parts)[:8000]
