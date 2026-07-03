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
from xml.etree import ElementTree as ET

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

_XMP_NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "photoshop": "http://ns.adobe.com/photoshop/1.0/",
    "xmpRights": "http://ns.adobe.com/xap/1.0/rights/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}

_XMP_DESCRIPTIVE_KEYS = {
    "dc:title": "title",
    "dc:description": "description",
    "dc:creator": "creator",
    "dc:subject": "keywords",
    "dc:rights": "rights",
    "dc:publisher": "publisher",
    "dc:date": "date",
    "photoshop:Credit": "credit",
    "photoshop:Source": "source",
    "xmpRights:UsageTerms": "rights",
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
        out.update(_parse_xmp(xmp))
    return out


def _qname(tag: str) -> str:
    if not tag.startswith("{"):
        return tag
    uri, local = tag[1:].split("}", 1)
    for prefix, ns in _XMP_NAMESPACES.items():
        if uri == ns:
            return f"{prefix}:{local}"
    return local


def _clean_text(value: Optional[str]) -> str:
    return " ".join((value or "").split())


def _xmp_value(node: ET.Element) -> Any:
    children = list(node)
    if not children:
        return _clean_text(node.text)
    for child in children:
        if _qname(child.tag) in {"rdf:Alt", "rdf:Seq", "rdf:Bag"}:
            values = [_clean_text(li.text) for li in child if _clean_text(li.text)]
            if _qname(child.tag) == "rdf:Alt" and values:
                return values[0]
            return values
    text = _clean_text(" ".join(node.itertext()))
    return text


def _parse_xmp(raw: str) -> dict:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        start = raw.find("<x:xmpmeta")
        end = raw.rfind("</x:xmpmeta>")
        if start == -1 or end == -1:
            return {}
        try:
            root = ET.fromstring(raw[start:end + len("</x:xmpmeta>")])
        except ET.ParseError:
            return {}

    fields: dict[str, Any] = {}
    for node in root.iter():
        for attr, value in node.attrib.items():
            key = _qname(attr)
            if key in _XMP_DESCRIPTIVE_KEYS and _clean_text(value):
                fields[key] = _clean_text(value)
        key = _qname(node.tag)
        if key in _XMP_DESCRIPTIVE_KEYS:
            value = _xmp_value(node)
            if value:
                fields[key] = value

    descriptive: dict[str, Any] = {}
    for xmp_key, desc_key in _XMP_DESCRIPTIVE_KEYS.items():
        value = fields.get(xmp_key)
        if not value:
            continue
        if desc_key == "keywords":
            if isinstance(value, str):
                value = [value]
            descriptive.setdefault(desc_key, value)
        else:
            descriptive.setdefault(desc_key, value[0] if isinstance(value, list) else value)

    return {"fields": fields, "descriptive": descriptive}


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

    # Build a descriptive layer that prefers IPTC, then XMP, then EXIF.
    iptc = result["iptc"]
    xmp_desc = (result["xmp"].get("descriptive") or {}) if isinstance(result["xmp"], dict) else {}
    exif = result["exif"]
    desc: dict[str, Any] = {}
    if iptc.get("title") or iptc.get("headline") or xmp_desc.get("title"):
        desc["title"] = iptc.get("title") or iptc.get("headline") or xmp_desc.get("title")
    if iptc.get("caption") or xmp_desc.get("description") or exif.get("ImageDescription"):
        desc["description"] = iptc.get("caption") or xmp_desc.get("description") or exif.get("ImageDescription")
    if iptc.get("creator") or xmp_desc.get("creator") or exif.get("Artist"):
        desc["creator"] = iptc.get("creator") or xmp_desc.get("creator") or exif.get("Artist")
    if iptc.get("copyright") or xmp_desc.get("rights") or exif.get("Copyright"):
        desc["rights"] = iptc.get("copyright") or xmp_desc.get("rights") or exif.get("Copyright")
    if iptc.get("keywords") or xmp_desc.get("keywords"):
        desc["keywords"] = iptc.get("keywords") or xmp_desc.get("keywords")
    if iptc.get("credit") or xmp_desc.get("credit"):
        desc["credit"] = iptc.get("credit") or xmp_desc.get("credit")
    if xmp_desc.get("publisher"):
        desc["publisher"] = xmp_desc["publisher"]
    if xmp_desc.get("date"):
        desc["date"] = xmp_desc["date"]
    result["descriptive"] = desc
    return result


def metadata_text(bundle: dict) -> str:
    """Flatten a metadata bundle into a searchable text blob for FTS."""
    parts: list[str] = []
    for section in ("descriptive", "iptc", "xmp", "exif"):
        data = bundle.get(section) or {}
        for k, v in data.items():
            if k == "raw":
                continue
            if isinstance(v, dict):
                v = " ".join(str(x) for x in v.values())
            if isinstance(v, (list, tuple)):
                v = " ".join(str(x) for x in v)
            parts.append(f"{k} {v}")
    return " ".join(parts)[:8000]
