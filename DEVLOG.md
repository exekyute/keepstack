# Devlog

Build notes in the order the work happened, kept for anyone who wants the
reasoning rather than just the result. Keepstack was built in a focused sprint, so
the entries are phases of that sprint rather than calendar days. Newest last.

## Phase 1: research before code

Started with research, before any code. Surveyed the twenty DAM systems that
matter most for government and institutional buyers, split them into the two
camps (standards-rich heritage tools and AI-rich photo libraries), and looked
for the empty intersection. The full study is in [RESEARCH.md](RESEARCH.md). The
decision that came out of it: the opportunity lived in the empty gap where
standards, AI, and easy self-hosting all meet.

## Phase 2: the shape of the thing

Turned the market gaps into ranked design goals (install-ease first, then free,
then standards, then optional AI, then governance). Chose the stack to serve
those goals rather than personal preference: SQLite so there is no database
server, content-addressable storage so dedup and fixity are one mechanism, a
zero-build frontend so self-hosting stays single-language. Each of these became
a decision record in [docs/decisions/](docs/decisions/).

## Phase 3: foundation up

Built bottom-up so each layer could be tested before the next leaned on it:
schema and config, then the content-addressable blob store, then metadata
extraction and thumbnails, then auth and the audit log. Writing storage before
ingest meant the dedup-and-fixity behavior was provable in isolation.

## Phase 4: the pipeline and search

Wired the ingest pipeline (store, dedup, extract, thumbnail, enrich, index) and
the three search modes (full-text, faceted, semantic). The insight that saved
work: embed each asset once at ingest, then vary only the query. The same
embeddings power semantic search and "more like this".

## Phase 5: standards and the API

Implemented Dublin Core, OAI-PMH, and IIIF from their specifications on the
standard library, then the FastAPI routes over everything, then the two-tone
web client. Kept the standards in the core so they are exercised by the same
tests as the rest, rather than rotting as an unused side feature.

## Phase 6: prove it, then be honest about it

Wrote the test suite, seeded synthetic demo data, and captured real screenshots
of the running app. Then graded Keepstack against seven competitors in
[COMPARISON.md](COMPARISON.md), with the grading checked against the actual
source so nothing on the roadmap got sold as shipped. The audit downgraded the
AI cells from "full" to "partial" (heuristic without a key), which is the
honest result and the more credible one.

## What I would do next

The gaps the comparison surfaced are the roadmap: a local vision model so AI
tagging is real with no key, OAIS format migration, a published accessibility
conformance report, OCR, and SSO. See [ROADMAP.md](ROADMAP.md).
