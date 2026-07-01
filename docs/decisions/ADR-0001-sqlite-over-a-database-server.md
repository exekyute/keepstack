# ADR-0001: SQLite over a database server

**Status:** accepted

## Context

The loudest, most consistent barrier to adopting the standards-rich DAMs is
operations. DSpace wants 6 to 8 GB of RAM and a Java, Solr, and Postgres stack.
Archivematica cannot be shipped as a click-through installer. If the goal is a
genuinely one-command install, the database is the first thing that gets in the
way, because a separate database server has to be provisioned, secured, tuned,
and backed up on its own.

## Decision

Use SQLite as the only datastore, in WAL mode, with the FTS5 extension for
full-text search. The entire catalog is a single file inside the data
directory, next to the blob store.

## Consequences

**Good.** No database server to run. The whole repository is one portable
directory you can copy, back up, or move. FTS5 gives real full-text search with
zero extra infrastructure. Tests run against a throwaway file. This is what
makes `python -m keepstack` and `docker compose up` actually one step.

**The cost.** SQLite handles the read-heavy, modest-write profile of a
self-hosted DAM well into the hundreds of thousands of assets, but very high
write concurrency would eventually want Postgres. The query and storage layers
are kept plain SQL and narrow so that a Postgres backend could be added later
without reshaping the application. Until a real deployment hits that ceiling,
paying the operational cost of a database server up front would be a poor trade.
