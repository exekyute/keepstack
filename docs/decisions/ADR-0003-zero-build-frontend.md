# ADR-0003: A zero-build frontend

**Status:** accepted

## Context

The install-ease goal does not stop at the backend. A frontend that needs an
npm install and a build step reintroduces exactly the toolchain friction the
project is trying to remove, and it makes self-hosting a two-language operation.

## Decision

Write the web client as plain HTML, one CSS file, and vanilla JavaScript, served
directly as static files by the same FastAPI process. No framework, no bundler,
no build.

## Consequences

**Good.** Self-hosting stays a single Python step; there is no Node toolchain to
install or keep current. The client is trivial to read and to hack on, which
suits an open-source project where a first contributor might just want to tweak
a view. Serving it from the API process means one port and no CORS setup.

**The cost.** No framework means no component ecosystem and more manual DOM
work, so a much larger UI would eventually justify a build step and a framework.
At the current scope (a library grid, a detail drawer, upload, and a few admin
views) the vanilla approach is a net win, and the two-tone design system lives
in CSS variables so the styling stays consistent without tooling.
