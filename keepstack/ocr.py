"""Optional OCR through the Tesseract command-line tool.

Keepstack shells out to the ``tesseract`` binary when it is installed, so
this adds no Python dependencies. When the binary is absent every function
degrades to a quiet no-op and ingest continues unaffected.
"""
from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

MAX_TEXT = 8000


@lru_cache(maxsize=1)
def available() -> bool:
    return shutil.which("tesseract") is not None


def extract_text(path: Path, timeout: int = 30) -> str:
    """Run Tesseract over an image and return whitespace-normalised text."""
    if not available():
        return ""
    try:
        proc = subprocess.run(
            ["tesseract", str(path), "stdout"],
            capture_output=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            return ""
        text = proc.stdout.decode("utf-8", "replace")
        return " ".join(text.split())[:MAX_TEXT]
    except Exception:
        return ""
