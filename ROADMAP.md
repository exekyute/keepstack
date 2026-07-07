# Roadmap

Keepstack ships a complete core today. What follows is the trajectory, and most of
it is the honest gaps from [COMPARISON.md](COMPARISON.md) turned into direction.
Checked items are built and verified; unchecked items are planned.

## Shipped (v0.1.0)

- [x] Upload with content-addressable deduplication and SHA-256 fixity
- [x] EXIF / IPTC / XMP extraction and thumbnails
- [x] Full-text (FTS5), faceted, and semantic search plus "more like this"
- [x] Collections, tags (manual and AI), and per-asset versioning
- [x] Four-role RBAC, audit log, and expiring/download-limited share links
- [x] Dublin Core, OAI-PMH 2.0, and IIIF Image API endpoints
- [x] Repository-wide fixity check
- [x] Optional, offline-capable AI (Groq vision, Cohere embeddings)
- [x] Two-tone web client and a full REST API

## Next: close the AI gap without a cloud dependency

- [x] In-process local vision model (small CLIP) so auto-tagging and semantic
      search are real with zero API keys, not just heuristic (#5)
- [ ] Approximate-nearest-neighbor index (sqlite-vec or pgvector) so semantic
      search scales past tens of thousands of assets
- [x] Local OCR (Tesseract) so scanned documents and text-in-image are findable (#4)

## Next: deepen the standards

- [x] IIIF Image API level 2: region, rotation, and best-fit sizing (contributed in #7)
- [x] IIIF Presentation API manifest (#15)
- [ ] OAI-PMH resumption tokens and selective harvesting by set
- [ ] METS packaging with embedded PREMIS events for preservation exchange
- [x] Parse XMP into structured fields rather than storing it raw (contributed in #8)

## Next: the government and compliance features

- [ ] Published Section 508 / WCAG 2.2 accessibility conformance report (VPAT)
- [ ] Full keyboard-and-screen-reader audit of the web client
- [ ] Legal hold and a disposition workflow on top of the retention field
- [ ] Non-destructive redaction derivatives for FOIA / public-records requests
- [ ] SSO (SAML / OIDC) and SCIM provisioning
- [ ] C2PA Content Credentials: read, validate, and preserve across edits

## Later: preservation and scale

- [ ] OAIS-style active format migration with a format policy registry
- [ ] Background workers for video transcoding and document rendering
- [x] Orphan-blob garbage collection via `python -m keepstack gc` (contributed in #6)
- [ ] Optional Postgres backend for high write concurrency

Have a use case that reorders this? Open an issue.
