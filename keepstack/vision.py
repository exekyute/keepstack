"""Optional on-device vision model (CLIP) for real semantic and visual search.

When the optional ``onnxruntime`` package is installed, Keepstack downloads a
small quantized CLIP model on first use and embeds text and images into one
shared vector space, entirely on-device: no API keys and no cloud calls.
Without the package every entry point returns None and callers fall back to
the deterministic lexical embedding in ``ai.py``.

Model: openai/clip-vit-base-patch32, int8-quantized ONNX export published at
https://huggingface.co/Xenova/clip-vit-base-patch32 (roughly 150 MB total,
cached under the data directory). Enable with ``pip install onnxruntime``
followed by ``python -m keepstack reindex``.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .config import config

_BASE = "https://huggingface.co/Xenova/clip-vit-base-patch32/resolve/main"
_FILES = {
    "text_model.onnx": f"{_BASE}/onnx/text_model_quantized.onnx",
    "vision_model.onnx": f"{_BASE}/onnx/vision_model_quantized.onnx",
    "vocab.json": f"{_BASE}/vocab.json",
    "merges.txt": f"{_BASE}/merges.txt",
}
_CONTEXT = 77
_state: dict = {}

# Curated nouns for zero-shot tagging; scored as "a photo of {label}".
TAG_LABELS = [
    "landscape", "cityscape", "building", "architecture", "people", "crowd",
    "food", "drink", "animal", "dog", "cat", "bird", "plant", "flower",
    "tree", "forest", "mountain", "beach", "ocean", "river", "lake", "sky",
    "sunset", "night", "snow", "road", "car", "boat", "airplane", "train",
    "bicycle", "map", "diagram", "chart", "document", "text", "poster",
    "logo", "artwork", "painting", "illustration", "screenshot", "furniture",
    "interior", "sports", "machine", "tool", "clothing", "toy",
    "abstract pattern",
]


def _model_dir() -> Path:
    override = os.environ.get("KEEPSTACK_MODEL_DIR")
    if override:
        return Path(override)
    return config.data_dir / "models" / "clip"


def runtime_available() -> bool:
    try:
        import onnxruntime  # noqa: F401
        return True
    except Exception:
        return False


def model_present() -> bool:
    d = _model_dir()
    return all((d / name).exists() for name in _FILES)


def ready() -> bool:
    """True when embeddings can be produced without any network access."""
    return runtime_available() and model_present()


def ensure_model() -> bool:
    """Download missing model files (idempotent). Returns readiness."""
    if not runtime_available():
        return False
    d = _model_dir()
    d.mkdir(parents=True, exist_ok=True)
    for name, url in _FILES.items():
        dest = d / name
        if dest.exists():
            continue
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            print(f"[keepstack] downloading {name} ...")
            with urllib.request.urlopen(url, timeout=180) as resp, open(tmp, "wb") as out:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            tmp.rename(dest)
        except Exception:
            tmp.unlink(missing_ok=True)
            return False
    return model_present()


# ---------------------------------------------------------------------------
# CLIP byte-pair-encoding tokenizer (standard library only)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _bytes_to_unicode() -> dict[int, str]:
    bs = (list(range(ord("!"), ord("~") + 1))
          + list(range(ord("\xa1"), ord("\xac") + 1))
          + list(range(ord("\xae"), ord("\xff") + 1)))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


class _Tokenizer:
    def __init__(self, vocab_path: Path, merges_path: Path) -> None:
        self.encoder = json.loads(vocab_path.read_text(encoding="utf-8"))
        lines = merges_path.read_text(encoding="utf-8").splitlines()
        merges = [tuple(m.split()) for m in lines if m and not m.startswith("#") and len(m.split()) == 2]
        self.bpe_ranks = {pair: i for i, pair in enumerate(merges)}
        self.byte_encoder = _bytes_to_unicode()
        self.cache: dict[str, list[str]] = {}
        self.pat = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d|[^\W\d_]+|\d|[^\s\w]+",
                              re.IGNORECASE | re.UNICODE)
        self.sot = self.encoder["<|startoftext|>"]
        self.eot = self.encoder["<|endoftext|>"]

    def _bpe(self, token: str) -> list[str]:
        if token in self.cache:
            return self.cache[token]
        word = tuple(token[:-1]) + (token[-1] + "</w>",)
        pairs = {(word[i], word[i + 1]) for i in range(len(word) - 1)}
        if not pairs:
            return [token + "</w>"]
        while True:
            bigram = min(pairs, key=lambda p: self.bpe_ranks.get(p, float("inf")))
            if bigram not in self.bpe_ranks:
                break
            first, second = bigram
            new_word: list[str] = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(first, i)
                except ValueError:
                    new_word.extend(word[i:])
                    break
                new_word.extend(word[i:j])
                i = j
                if i < len(word) - 1 and word[i] == first and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            word = tuple(new_word)
            if len(word) == 1:
                break
            pairs = {(word[i], word[i + 1]) for i in range(len(word) - 1)}
        out = list(word)
        self.cache[token] = out
        return out

    def encode(self, text: str) -> list[int]:
        text = " ".join((text or "").lower().strip().split())
        ids = [self.sot]
        for tok in self.pat.findall(text):
            mapped = "".join(self.byte_encoder[b] for b in tok.encode("utf-8"))
            for piece in self._bpe(mapped):
                pid = self.encoder.get(piece)
                if pid is not None:
                    ids.append(pid)
            if len(ids) >= _CONTEXT - 1:
                break
        return ids[: _CONTEXT - 1] + [self.eot]


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
def _sessions() -> dict:
    if "text" not in _state:
        import numpy as np
        import onnxruntime as ort
        d = _model_dir()
        opts = ort.SessionOptions()
        opts.log_severity_level = 3
        _state["np"] = np
        _state["text"] = ort.InferenceSession(str(d / "text_model.onnx"), opts,
                                              providers=["CPUExecutionProvider"])
        _state["vision"] = ort.InferenceSession(str(d / "vision_model.onnx"), opts,
                                                providers=["CPUExecutionProvider"])
        _state["tok"] = _Tokenizer(d / "vocab.json", d / "merges.txt")
    return _state


def _run(session, feeds, np) -> list[float]:
    names = {i.name for i in session.get_inputs()}
    out = session.run(None, {k: v for k, v in feeds.items() if k in names})[0]
    if out.ndim == 3:  # (batch, seq, dim) hidden states: take the first token
        out = out[:, 0, :]
    vec = out[0].astype("float32")
    norm = float(np.linalg.norm(vec)) or 1.0
    return (vec / norm).tolist()


def embed_text(text: str) -> Optional[list[float]]:
    if not ready():
        return None
    try:
        st = _sessions()
        np = st["np"]
        ids = st["tok"].encode(text)
        # The export takes dynamic-length input_ids and pools internally, so
        # padding would move the pooled end-of-text position: feed exact length.
        feeds = {"input_ids": np.array([ids], dtype=np.int64)}
        return _run(st["text"], feeds, np)
    except Exception:
        return None


def embed_image(path: Path) -> Optional[list[float]]:
    if not ready():
        return None
    try:
        from PIL import Image
        st = _sessions()
        np = st["np"]
        with Image.open(path) as img:
            img = img.convert("RGB")
            scale = 224 / min(img.size)
            img = img.resize((max(224, round(img.width * scale)),
                              max(224, round(img.height * scale))), Image.BICUBIC)
            left = (img.width - 224) // 2
            top = (img.height - 224) // 2
            img = img.crop((left, top, left + 224, top + 224))
            arr = np.asarray(img, dtype=np.float32) / 255.0
        mean = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
        std = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)
        pixel = ((arr - mean) / std).transpose(2, 0, 1)[None, ...]
        return _run(st["vision"], {"pixel_values": pixel}, np)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _label_embeds() -> list[Optional[list[float]]]:
    return [embed_text(f"a photo of {label}") for label in TAG_LABELS]


def zero_shot_tags(image_vec: Optional[list[float]], top_k: int = 6,
                   min_score: float = 0.22) -> list[tuple[str, float]]:
    """Rank the curated labels against an image embedding (both normalised)."""
    if not image_vec:
        return []
    scored = []
    for label, vec in zip(TAG_LABELS, _label_embeds()):
        if vec:
            scored.append((label, sum(a * b for a, b in zip(image_vec, vec))))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(label, round(score, 3)) for label, score in scored[:top_k] if score >= min_score]
