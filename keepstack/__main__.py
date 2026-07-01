"""Run Keepstack: ``python -m keepstack`` (optionally ``... seed`` first).

Environment:
  KEEPSTACK_HOST (default 0.0.0.0)   KEEPSTACK_PORT (default 8000)
"""
from __future__ import annotations

import json
import os
import sys

import uvicorn


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        from .seed import run_seed
        run_seed()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "gc":
        from .db import init_db
        from .storage import collect_orphan_blobs

        init_db()
        result = collect_orphan_blobs(dry_run="--dry-run" in sys.argv[2:])
        print(json.dumps(result, indent=2))
        return
    host = os.environ.get("KEEPSTACK_HOST", "0.0.0.0")
    port = int(os.environ.get("KEEPSTACK_PORT", "8000"))
    uvicorn.run("keepstack.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
