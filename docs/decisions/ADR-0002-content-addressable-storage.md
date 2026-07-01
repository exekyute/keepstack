# ADR-0002: Content-addressable storage

**Status:** accepted

## Context

A DAM needs three things from its storage that are usually built separately:
deduplication (do not store the same file twice), integrity (prove a file has
not rotted), and a foundation for digital preservation (fixity checks over
time). Building each as its own feature is more code and more ways to drift out
of sync.

## Decision

Store every blob by its SHA-256 hash. The hash is the storage key: a file lands
at `blobs/<aa>/<bb>/<full-sha256>`. Before writing, hash the incoming bytes; if
that hash already exists, reuse the existing blob instead of writing a copy.

## Consequences

**Good.** Deduplication is automatic: two uploads of the same bytes collapse to
one blob with no special logic. Integrity is free: re-hashing a stored blob and
comparing to its recorded key is a complete fixity check, which is the core of
digital preservation. One decision paid for three features. The first four hex
characters fan out into nested directories so a single folder never holds
millions of files.

**The cost.** Content addressing means a blob is immutable, so "editing" an
asset's bytes creates a new blob and a new version rather than mutating in
place, which is why versioning is modeled as new content rather than diffs. Hash
computation adds a streaming pass over each upload, which is negligible next to
the network transfer. Orphan blobs (no asset references them) need occasional
garbage collection, which the storage layer supports but does not yet schedule.
