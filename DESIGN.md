# Design notes: the market, the gap, and how Keepstack is built

This document explains why Keepstack exists: what the DAM market looks like in 2026,
where the gap is, the decisions that followed, and an honest account of what
works and what does not yet. If you only read one document in this repository,
read this one. It links out to the deeper material as you go.

- Want the raw market research? See [RESEARCH.md](RESEARCH.md).
- Want the head-to-head scoring? See [COMPARISON.md](COMPARISON.md).
- Want to understand the code? See [ARCHITECTURE.md](ARCHITECTURE.md).
- New to the domain? Start with the [DAM-101 primer](docs/DAM-101.md).

---

## TL;DR

The digital asset management market splits into two camps that never met.
Standards-rich archival tools have deep metadata and preservation but archaic
interfaces and no AI. Modern AI photo libraries have great search and UX but no
archival standards at all. No open-source tool occupies the intersection.
Keepstack is built to sit exactly there: archival standards plus modern local AI
plus a clean interface, installable in one command, free and self-hostable. It
is honest about the ground it has not taken yet (enterprise AI depth,
preservation format migration, a published accessibility conformance report).

---

## 1. The state of DAM in 2026

I surveyed the twenty systems that matter most for public-sector, archival, and
institutional buyers, a mix of commercial and open-source. The full,
citation-backed study is in [RESEARCH.md](RESEARCH.md); here is the shape of it.

**Camp A: standards-rich heritage and preservation tools.** ResourceSpace,
CollectiveAccess, Omeka, DSpace, Islandora, Fedora, Archivematica, Axiell, and
Preservica. These run national archives, libraries, and museums (the UK
National Archives, the World Bank, the Smithsonian, the UN). They speak Dublin
Core, METS, PREMIS, EAD, MARC, OAI-PMH, and IIIF. They are also, by common
account, hard to install (DSpace wants 6 to 8 GB of RAM, Archivematica cannot be
shipped as a click-through installer), dated in the interface, and almost
entirely without AI.

**Camp B: AI-rich, modern-UX media libraries.** Immich, PhotoPrism, LibrePhotos,
and the commercial leaders Bynder and Adobe. Great tagging, semantic search, and
clean interfaces. But the open-source ones have no Dublin Core, no OAI-PMH, no
IIIF, and no preservation formats, and the commercial ones are neither free nor
self-hostable.

**What the whole field complains about,** regardless of camp: opaque or
per-seat pricing, painful installs, weak search, a near-universal absence of a
published Section 508 / WCAG accessibility report, records retention locked
behind the priciest tiers, and vendor lock-in.

---

## 2. The gap

Put the two camps on the same axes and the hole is obvious.

|  | Archival standards | Modern AI + UX | Free + easy self-host |
|--|:--:|:--:|:--:|
| Heritage tools (DSpace, Archivematica) | yes | no | partly |
| AI photo libraries (Immich, PhotoPrism) | no | yes | yes |
| Commercial leaders (Adobe, Bynder) | some | yes | no |
| **The empty intersection** | **yes** | **yes** | **yes** |

No open-source tool holds all three corners. That intersection is the thesis.

---

## 3. What "better" had to mean

The gaps in section 1 became the design goals, in priority order. This is the
part that turns a complaint list into a build.

1. **Install in one command.** The single biggest adoption barrier, so it is
   goal number one, not a footnote.
2. **Free with no per-seat tax.** The loudest complaint, and the natural home
   advantage of open source.
3. **Standards in the core, not a paid edition.** Dublin Core, EXIF/IPTC/XMP,
   OAI-PMH, IIIF, and fixity, all shipped.
4. **AI that is free and works offline,** upgrading in quality when you add a
   key, never required.
5. **Governance most tools paywall:** roles, an audit trail, expiring shares,
   retention, and an open API so data is never trapped.
6. **Honesty about the boundary.** No FedRAMP, no generative image editing.
   Aim at state and local government, education, museums, archives, and NGOs,
   where cost, standards, and sovereignty are the binding constraints.

---

## 4. The decisions that followed

Each of these has a short decision record in
[docs/decisions/](docs/decisions/) explaining the context and the tradeoff.

- **SQLite, not a database server** ([ADR-0001](docs/decisions/ADR-0001-sqlite-over-a-database-server.md)). The whole catalog is one portable file. Nothing to provision or secure separately, which is what makes the one-command install real.
- **Content-addressable storage** ([ADR-0002](docs/decisions/ADR-0002-content-addressable-storage.md)). Files are keyed by their SHA-256 hash, so identical uploads collapse to one blob and integrity is verifiable at any time. Deduplication and digital-preservation fixity fall out of the same decision.
- **A zero-build frontend** ([ADR-0003](docs/decisions/ADR-0003-zero-build-frontend.md)). Plain HTML, CSS, and JavaScript, no npm toolchain, so self-hosting never requires a Node build.
- **Optional, offline-capable AI** ([ADR-0004](docs/decisions/ADR-0004-optional-offline-ai.md)). Every AI feature has a deterministic local fallback, so the product is fully useful with zero API keys and adds no dependencies to enable.
- **Standards as core, not an add-on** ([ADR-0005](docs/decisions/ADR-0005-standards-as-core.md)). Dublin Core, OAI-PMH, and IIIF ship for every asset, because that is the whole reason the heritage buyers pay incumbents.

---

## 5. What I built

A working system, not a prototype. Details in [ARCHITECTURE.md](ARCHITECTURE.md).

- Upload with automatic deduplication, EXIF/IPTC/XMP extraction, and thumbnails
- Full-text (SQLite FTS5), faceted, and embedding-based semantic search
- Collections, tags (manual and AI), and per-asset versioning
- Four-role access control, an audit log on every change, and expiring share links
- Dublin Core, an OAI-PMH 2.0 endpoint, and an IIIF Image API endpoint per asset
- A one-click repository-wide fixity check for integrity
- A clean two-tone web client and a REST API for everything

Four runtime dependencies. One command to run.

---

## 6. Does it actually work

Verification, not assertion.

- **Tests:** the core pipeline (ingest, dedup, search, semantic ranking, fixity
  detecting corruption, Dublin Core, OAI-PMH) has a passing suite.
- **Screenshots:** real captures of the running app are in
  [docs/screenshots/](docs/screenshots/).
- **Semantic search, checked:** a query for "coastal environment water" ranks the
  coastal-survey and watershed assets to the top.
- **Integrity, checked:** corrupt a stored blob and the fixity check flags it.

---

## 7. Honest assessment

The full head-to-head is in [COMPARISON.md](COMPARISON.md), graded against the
source code and audited for overclaiming. The short version:

**Where Keepstack leads:** it is the only column that is free, self-hostable,
standards-native, and governance-complete at once. Install, cost, open
standards, integrity/dedup, and audit are clear wins.

**Where Keepstack trails today, on purpose:** the best AI tier needs one
optional install (a local CLIP model, no API keys) and the minimal install is
heuristic; preservation is fixity but not yet format migration; accessibility
has alt-text but no published VPAT; there is no SSO yet. Adobe, Preservica,
and Orange Logic beat it on those.

Marking those gaps plainly is deliberate. A comparison that cannot admit a
weakness is not trustworthy, and the gaps are the roadmap.

---

## 8. What I learned

The biggest lesson was that the opening was structural. I did not set out to add
a missing feature. What I found was that two mature groups of tools had never
been combined, and the space between them was empty, and that reframing mattered
more than any single capability.

The standards surprised me. Dublin Core, OAI-PMH, and IIIF are a few hundred
lines each on the standard library, and yet they are the thing museums and
archives pay incumbents for. Supporting them well was mostly a matter of
deciding to.

Content-addressable storage was the choice that paid off most, because it gave
deduplication, integrity checking, and preservation fixity all at once.

The part I am most sure about is the honesty. The most credible thing in the
project is the column in the comparison that shows where Keepstack loses.

---

## 9. What's next

The roadmap is in [ROADMAP.md](ROADMAP.md), and it is mostly the honest gaps
above, turned into direction: local OCR and a real vision model, OAIS format
migration, a published accessibility conformance report, SSO, and deeper IIIF.

If you want to follow the build reasoning as it happened, the
[DEVLOG.md](DEVLOG.md) has the dated notes.
