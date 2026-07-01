# How Keepstack compares

A two-column `Feature | Why` table can only assert that a tool is better. It
names no competitor, shows no evidence, and structurally cannot admit a
weakness, which is exactly why buyers distrust it. So this is a **capability
matrix** instead: Keepstack next to seven leading systems, graded on the same 21
capabilities, including the rows where Keepstack is only partial or still on the
roadmap. It shows the gap rather than claiming it.

**How it was graded.** Every Keepstack cell was checked against the actual source
code in this repository. Every competitor cell was graded against the
citation-backed research in [`docs/research/`](docs/research/) and
[`RESEARCH.md`](RESEARCH.md). The grades were then put through adversarial
honesty and fairness auditors before being recorded here.

**Legend:** ✓ full   ◐ partial   $ paywalled (paid tier only)   ◔ roadmap / planned   ✗ none   · not stated in the research

## The matrix

| Capability | Why it matters | Keepstack | ResourceSpace | DSpace | Immich | Bynder | Adobe AEM | Preservica | Orange Logic |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| One-command install | Hard installs are the #1 reason OSS DAM projects stall | ✓ | ◐ | ✗ | ✓ | ✗ | ✗ | · | ✗ |
| Free, no per-seat pricing | Per-seat / metered pricing is the loudest buyer complaint | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ◐ | ✗ |
| Self-host / data sovereignty | Agencies and archives often cannot use multi-tenant SaaS | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ◐ | ◐ |
| Open API / no lock-in | Full export and open formats protect data over decades | ✓ | ✓ | · | ✓ | · | · | · | · |
| Dublin Core metadata | Baseline descriptive standard, mandatory for OAI-PMH | ✓ | ✓ | ✓ | ✗ | · | · | ✓ | · |
| EXIF / IPTC / XMP extraction | Archival workflows depend on embedded metadata fidelity | ◐ | ✓ | ◐ | ◐ | ◐ | ✓ | · | · |
| OAI-PMH harvesting | Lets aggregators (DPLA, Europeana) mirror the catalog | ✓ | ✓ | ✓ | ✗ | ✗ | · | ✓ | · |
| IIIF Image API | Standard deep-zoom delivery from one master | ◐ | · | ✓ | ✗ | ✗ | · | ✓ | · |
| Digital preservation (fixity) | Assets verifiably readable in 50+ years | ◐ | · | ◐ | ✗ | ✗ | · | ✓ | ✓ |
| Content-addressable dedup | Stores identical content once; integrity by hash | ✓ | · | · | ✓ | ◐ | · | · | · |
| AI auto-tagging | Closes the gap when humans upload without tagging | ◐ | ✓ | ✗ | ✓ | $ | ✓ | · | ✓ |
| Semantic / NL search | Finds assets nobody tagged | ◐ | ◐ | ◔ | ✓ | $ | ✓ | · | ✓ |
| Faceted + full-text search | Precise drill-down retrieval, the moment of truth | ✓ | ✓ | ◐ | ◐ | ✓ | ✓ | · | ✓ |
| OCR / text-in-image | Makes scanned documents findable | ◔ | ✓ | · | · | $ | ✓ | · | · |
| Asset versioning | Change history plus revert / audit | ✓ | ✓ | ✓ | ✗ | ✓ | · | · | · |
| Role-based access control | Per-role permissions are governance table stakes | ✓ | ✓ | ✓ | ◐ | ✓ | ✓ | · | ✓ |
| Audit log / chain of custody | Regulated buyers require a who-did-what trail | ✓ | · | · | · | · | · | ✓ | ✓ |
| Controlled / expiring shares | Distribute approved assets without losing control | ✓ | · | · | ◐ | ✓ | · | ◐ | · |
| Records retention / legal hold | Government records carry mandated retention rules | ◐ | · | · | ✗ | · | · | ✓ | ◐ |
| Accessibility (alt-text + VPAT) | A 508/WCAG VPAT is a hard procurement gate | ◐ | · | ✗ | · | ✗ | ✓ | ✓ | ✓ |
| SSO (SAML/OIDC) / SCIM | Enterprise identity integration | ◔ | · | · | ◐ | ✓ | ✓ | ✓ | ✓ |

"Not stated" (·) means the research did not establish the capability either
way. It is not the same as "none".

## Where Keepstack wins, and why

No other column is `full` across all of free, self-hostable, standards-native
(Dublin Core + OAI-PMH), and governance (versioning + RBAC + audit + expiring
shares + open API). The standards-rich tools are not free-and-easy and have no
AI; the AI photo libraries have no standards; the commercial leaders are not
free or self-hostable. Keepstack is the only one holding all four corners at once.

| Where Keepstack leads | How it does it | Why that beats the field |
|---|---|---|
| Install and operate | One `pip install` or `docker compose up`, four runtime deps, SQLite, no build step | The heritage tools (DSpace 6 to 8 GB RAM, Archivematica, CollectiveAccess) are the hardest part of adopting them |
| Cost model | MIT, no seats, no metering, no overage outage | Every commercial column is quote-only, per-seat, or credit-metered, the loudest complaint in the market |
| Standards in the core | Dublin Core, EXIF/IPTC/XMP, OAI-PMH, IIIF shipped, not a paid edition | Commercial DAMs gate these as museum-only add-ons; the photo libraries have none |
| Integrity and dedup | Content-addressable SHA-256 with a one-click repository fixity check | A free, verifiable integrity story most columns do not state at all |
| Governance | Four-role RBAC, audit log on every change, expiring/limited share links, full REST API | The capabilities incumbents reserve for their top paid tier |

## Where Keepstack honestly trails today

The matrix marks these `partial`, `roadmap`, or `none` on purpose:

- **AI is real but conditional.** Out of the box, auto-tagging is colour and
  orientation heuristics, and semantic search is a lexical embedding. True
  vision tagging and learned semantic search need an optional Groq or Cohere
  key. Immich (local CLIP), Adobe (Sensei/Firefly), and Bynder lead here.
- **Preservation is fixity, not format migration.** Keepstack verifies integrity
  but does not yet do OAIS active format migration. Preservica and Orange
  Logic are purpose-built for that.
- **Accessibility has no published VPAT yet.** Alt-text is first-class and
  AI-suggested, but a formal 508/WCAG conformance report is on the roadmap.
  Adobe, Preservica, and Orange Logic publish one.
- **No OCR, no SSO/SCIM yet.** Both are on the roadmap. Enterprise columns
  ship them today.
- **IIIF and embedded-metadata depth are basic.** IIIF is level-1 images only;
  XMP is stored but not fully parsed.

These are the right gaps for a young project to have: the foundation, the
standards, and the governance are in place, and the items above are additive
rather than architectural. See the roadmap in [README.md](README.md).
