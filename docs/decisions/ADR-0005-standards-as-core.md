# ADR-0005: Open standards as core, not an add-on

**Status:** accepted

## Context

The research showed that open metadata standards (Dublin Core, OAI-PMH, IIIF,
and the archival stack) are treated as premium add-ons or museum-only editions
by the commercial DAMs, and are missing entirely from the AI photo libraries.
Yet these standards are the single biggest reason museums, libraries, and
archives pay incumbent prices. They are also, individually, small to implement.

## Decision

Ship the standards in the core product for every asset, not behind a flag or an
edition: Dublin Core mapping, an OAI-PMH 2.0 harvesting endpoint, and an IIIF
Image API endpoint. Implement them from the specifications on the standard
library so they add no dependencies.

## Consequences

**Good.** A free tool now speaks the language GLAM institutions require, which
is the whole competitive thesis. Any aggregator can harvest the catalog over
OAI-PMH, and any IIIF viewer can deep-zoom the images. Because the standards are
core, they are exercised by the same tests and screenshots as everything else,
so they do not rot as an unused side feature.

**The cost.** Standards have depth, and the current implementations are the
useful subset, not the full specifications: IIIF is Image API level 1 for images
only, OAI-PMH covers the core verbs with `oai_dc`, and the heavier archival
packaging (METS, PREMIS, EAD) is not built. Those are marked partial in
[COMPARISON.md](../../COMPARISON.md) and tracked in [ROADMAP.md](../../ROADMAP.md).
Shipping the high-value subset now beats shipping nothing while chasing
completeness.
