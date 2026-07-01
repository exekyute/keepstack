# ADR-0004: Optional, offline-capable AI

**Status:** accepted

## Context

AI in the DAM market is either paywalled (Bynder, Adobe), or dependent on an
external cloud API, or absent entirely in the standards-rich tools. A free tool
could differentiate on AI, but requiring an API key or a heavy GPU dependency
would undercut the "runs with zero configuration" promise and add a dependency
to enable.

## Decision

Make every AI feature pluggable and optional, with a deterministic local
fallback, reached through the standard library only. Auto-tagging falls back to
colour and orientation heuristics; semantic search falls back to a lexical
hashing embedding. When a Groq (vision) or Cohere (embeddings) key is present,
the same code path transparently upgrades to the real model.

## Consequences

**Good.** The product is fully useful with no keys and no extra dependencies:
tagging, semantic ranking, and captioning all do something out of the box.
Enabling real AI is a config change, not an install. Providers are called with
`urllib`, so turning AI on adds nothing to the dependency list.

**The cost, stated plainly.** Out of the box the "semantic" search is a lexical
embedding, not a learned one, and the auto-tags are heuristics, not vision.
Those are honestly marked as partial in [COMPARISON.md](../../COMPARISON.md).
The design choice was to make the capability present and free everywhere, and
excellent where a key is added, rather than to make it excellent but gated. A
future local model (for example a small CLIP running in-process) would close
the gap without a cloud dependency, and is on the roadmap.
