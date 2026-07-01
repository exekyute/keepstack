# Changelog

All notable changes to Keepstack are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
semantic versioning.

## [Unreleased]

### Added

- Advertise IIIF Image API level 2 and support region cropping, percent
  regions, best-fit sizing, and rotation for IIIF image requests.

## [0.1.0] - 2026-06-28

The first working release. A complete DAM core, built to sit in the gap between
standards-rich heritage tools and modern AI photo libraries.

### Added

- Content-addressable blob storage with automatic deduplication and SHA-256 fixity
- Ingest pipeline with EXIF / IPTC / XMP extraction and thumbnail generation
- Search: SQLite FTS5 full-text, faceted filtering, and embedding-based semantic
  search with a "more like this" mode
- Collections, tags (manual and AI-suggested), and per-asset version history
- Four-role access control (admin, editor, contributor, viewer), an audit log on
  every state change, and tokenised expiring share links
- Open standards: Dublin Core mapping, an OAI-PMH 2.0 endpoint, and an IIIF
  Image API endpoint for every asset
- A repository-wide fixity check for digital-preservation integrity
- Optional AI enrichment (Groq vision, Cohere embeddings) with deterministic
  offline fallbacks, so the product is fully useful with zero API keys
- A zero-build two-tone web client and a REST API covering every resource
- A passing test suite, synthetic seed data, and a Docker deployment

### Known limitations

Tracked in [ROADMAP.md](ROADMAP.md) and graded honestly in
[COMPARISON.md](COMPARISON.md): AI is heuristic without a provider key,
preservation is fixity rather than format migration, IIIF is level 1, and there
is no OCR, SSO, or published accessibility conformance report yet.
