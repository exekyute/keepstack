"""Optional, pluggable AI enrichment.

Design rule: Keepstack must be fully useful with zero API keys. Every AI
feature has a deterministic, offline local fallback so semantic search,
auto-tagging, and captioning all *work* out of the box, then transparently
upgrade in quality when a provider key is configured.

Providers are reached with stdlib ``urllib`` only, so enabling AI adds no
Python dependencies.

  - Embeddings:  Cohere (embed-v4) -> local hashing embedding fallback
  - Vision tags: Groq (llama vision) -> local colour/shape heuristics fallback
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import urllib.request
from pathlib import Path
from typing import Optional

from .config import config

EMBED_DIM = 256
_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Basic colour reference for the offline auto-tagger.
_COLORS = {
    "red": (200, 40, 40), "orange": (220, 130, 40), "yellow": (225, 210, 70),
    "green": (60, 160, 80), "blue": (60, 110, 200), "purple": (130, 70, 180),
    "pink": (230, 130, 180), "brown": (120, 80, 50), "black": (25, 25, 25),
    "white": (240, 240, 240), "gray": (128, 128, 128),
}


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------
def _local_embed(text: str) -> list[float]:
    """Deterministic hashing embedding: tokens -> buckets -> L2 normalised.

    This is a lexical vector, not a learned semantic one, but it makes
    similarity / "more like this" search work offline and ranks shared
    vocabulary sensibly.
    """
    vec = [0.0] * EMBED_DIM
    for tok in _TOKEN_RE.findall(text.lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % EMBED_DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cohere_embed(text: str) -> Optional[list[float]]:
    if not config.cohere_api_key:
        return None
    try:
        req = urllib.request.Request(
            "https://api.cohere.com/v2/embed",
            data=json.dumps({
                "model": "embed-v4.0",
                "texts": [text[:8000]],
                "input_type": "search_document",
                "embedding_types": ["float"],
            }).encode(),
            headers={
                "Authorization": f"Bearer {config.cohere_api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        return data["embeddings"]["float"][0]
    except Exception:
        return None


def embed(text: str) -> list[float]:
    from . import vision as _vision
    if _vision.ready():
        vec = _vision.embed_text(text)
        if vec:
            return vec
    if config.ai_enabled:
        vec = _cohere_embed(text)
        if vec:
            return vec
    return _local_embed(text)


def embed_image(path: Path) -> Optional[list[float]]:
    """Visual embedding in the shared CLIP space, when the local model is installed."""
    from . import vision as _vision
    if _vision.ready():
        return _vision.embed_image(path)
    return None


def pack_embedding(vec: list[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *vec)


def unpack_embedding(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"<{n}f", blob))


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


# ---------------------------------------------------------------------------
# Auto-tagging / captioning
# ---------------------------------------------------------------------------
def _local_image_tags(path: Path) -> list[tuple[str, float]]:
    """Offline heuristics: orientation, brightness, dominant colours."""
    try:
        from PIL import Image
        with Image.open(path) as img:
            img = img.convert("RGB")
            w, h = img.size
            tags: list[tuple[str, float]] = []
            ratio = w / h if h else 1
            if ratio > 1.25:
                tags.append(("landscape", 0.9))
            elif ratio < 0.8:
                tags.append(("portrait", 0.9))
            else:
                tags.append(("square", 0.8))

            avg = img.resize((1, 1), Image.BILINEAR).getpixel((0, 0))  # average colour
            avg = avg[:3] if isinstance(avg, tuple) else (avg, avg, avg)
            brightness = sum(avg) / 3
            if brightness < 70:
                tags.append(("dark", 0.7))
            elif brightness > 185:
                tags.append(("bright", 0.7))

            # nearest dominant colour
            best, best_d = None, 1e9
            for name, ref in _COLORS.items():
                d = sum((avg[i] - ref[i]) ** 2 for i in range(3))
                if d < best_d:
                    best, best_d = name, d
            if best:
                tags.append((best, 0.6))
            return tags
    except Exception:
        return []


def _groq_vision(path: Path, mime: str) -> Optional[dict]:
    if not (config.ai_enabled and config.groq_api_key):
        return None
    try:
        import base64
        b64 = base64.b64encode(path.read_bytes()).decode()
        prompt = (
            "You are a digital asset cataloguer. Return STRICT JSON: "
            '{"caption": "<one factual sentence>", "alt_text": "<accessibility '
            'description>", "tags": ["lowercase", "keywords"]}. No prose.'
        )
        body = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {config.groq_api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception:
        return None


def enrich_image(path: Path, mime: str) -> dict:
    """Return {caption, alt_text, tags:[(name, confidence)]}."""
    result = {"caption": "", "alt_text": "", "tags": []}
    remote = _groq_vision(path, mime)
    if remote:
        result["caption"] = (remote.get("caption") or "")[:500]
        result["alt_text"] = (remote.get("alt_text") or "")[:500]
        result["tags"] = [(str(t).lower().strip(), 0.85) for t in remote.get("tags", []) if t][:15]
        return result
    from . import vision as _vision
    if _vision.ready():
        tags = _vision.zero_shot_tags(_vision.embed_image(path))
        if tags:
            result["tags"] = tags
            return result
    result["tags"] = _local_image_tags(path)
    return result
