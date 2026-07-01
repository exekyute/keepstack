# DAM Feature Taxonomy, Standards, AI, and Compliance (research source)

Compiled June 2026 via live web research (five parallel agents). Condensed,
citation-backed reference feeding `RESEARCH.md`. This is the "what makes a DAM
good" backbone.

## 1. Core feature taxonomy (11 functions)
1. **Ingest**: bulk drag-drop, smart routing rules on arrival, FTP/SFTP, API, CSV/batch, watch folders, duplicate "waiting room" (Bynder). Leaders: Brandfolder, Bynder.
2. **Storage**: versioning, deduplication, **content-addressable storage** (hash = key, identical content stored once), S3 versioning + object-lock/WORM, tiered/cold storage, pluggable backends (Pimcore Flysystem).
3. **Metadata**: custom schemas + field types, controlled vocabularies/taxonomies, auto-extract EXIF/IPTC/XMP on ingest, AI-generated fields, cascading/inheritance, bulk edit. Leaders: Adobe AEM (Sensei), Pimcore, ResourceSpace.
4. **Search**: faceted/filtered, full-text + OCR, saved searches, Boolean/query builder, **AI/semantic/natural-language**, visual similarity/reverse image, face search. Leader: Cloudinary.
5. **Organization**: folders (3-5 levels), static + dynamic/smart collections, lightboxes, tags. Canonical model: folders=storage, keywords=content, collections=grouping.
6. **Rendition/transform**: thumbnails + 200+ format preview, **on-the-fly crop/resize via URL params**, format conversion + auto-optimization (AVIF/WebP), video transcoding, smart crop, presets. Leader: Cloudinary, AEM Dynamic Media.
7. **Distribution**: share links + embed, **branded portals with two-way sync**, public/private galleries, CDN delivery + per-link analytics. Leader: MediaValet.
8. **Rights/DRM**: usage rights + license tracking, expiry/embargo, static + dynamic watermarking, model/property releases, copyright + provenance. Leaders: Orange Logic, Aprimo, FotoWare.
9. **Workflow/collaboration**: approval routing, in-context annotation/markup, task assignment, comments + notifications. Leaders: Bynder, Frontify.
10. **Administration**: RBAC, SSO (SAML/OIDC), SCIM provisioning, audit logs, quotas, retention. Build order: RBAC -> audit -> SSO -> SCIM.
11. **Integrations/API**: REST + GraphQL, webhooks, creative-tool plugins (Adobe CC, Figma), CMS/commerce/Office connectors, Zapier/no-code, OAuth2. Leader: Cloudinary, Pimcore.

## 2. Metadata and interoperability standards
- **EXIF** (CIPA DC-008, v3.0 2023): camera capture provenance, orientation, GPS (stripped before public release for privacy).
- **IPTC Photo Metadata** (Core + Extension): descriptive/rights/admin standard for pro imagery. Carries Creator/Copyright/Credit/Caption/Keywords + licensing, model releases, **Alt Text + Extended Description accessibility fields (2021.1)**, and **AI-provenance fields (2023.1/2025.1)**. Serialized as legacy IIM and modern XMP (root of sync bugs). Effectively mandatory at AP/Reuters/Getty/BBC. Sibling: **IPTC Video Metadata Hub**.
- **XMP** (ISO 16684-1): XML/RDF container hosting Dublin Core, IPTC, rights as RDF triples; embeds or lives as sidecar `.xmp` (norm for RAW). DAM must support both + two-way sync.
- **Dublin Core** (DCMI): 15-element cross-domain vocabulary; **mandatory baseline for OAI-PMH (oai_dc)**.
- **Preservation/archival stack**: **PREMIS v3** (preservation events, fixity, the audit trail of a system of record), **METS** (XML package wrapper, SIP/AIP/DIP), **MODS** (MARC-derived bibliographic), **EAD3** (archival finding aids, hierarchical).
- **Delivery/harvesting**: **IIIF** (Image API 3.0 parameterized `{id}/{region}/{size}/{rotation}/{quality}.{format}` from one master; Presentation API JSON-LD manifests; highest-leverage GLAM delivery standard), **OAI-PMH 2.0** (six-verb harvesting, cheapest federation path to DPLA/Europeana), **Schema.org** ImageObject JSON-LD.
- **Controlled vocabularies**: Getty AAT/TGN/ULAN, Library of Congress LCSH/LCNAF, MARC. Store **URIs** alongside labels.
- **C2PA / Content Credentials** (v2.2, 2025): cryptographically verifiable provenance "nutrition label"; **CISA endorsed Jan 2025**; Reuters+Canon production workflow live.
- **Mandates**: US federal records (NARA 36 CFR 1236 Subpart E + PREMIS); GLAM (MODS/MARC + METS + PREMIS + EAD3 + OAI-PMH + IIIF + authority control); news (IPTC mandatory).
- **Design-critical**: embedded vs sidecar (support both, keep synced); IPTC IIM/XMP dual-encoding (Get-Edit-Replace, XMP authoritative); **metadata loss on transformation is a widespread failure** (resizing strips IPTC/EXIF; every derivative path must copy forward rights/descriptive blocks + honor orientation + preserve C2PA).

## 3. AI / ML capabilities
Key insight: most commercial DAMs orchestrate third-party cloud APIs (AWS Rekognition, Google Vision, Azure); real model-builders are Adobe (Sensei/Firefly), Aprimo, Brandfolder. **Architectural core: embed every asset once at ingest, store vectors in an HNSW index, vary only the query** (text->semantic, image->visual similarity, image+tight threshold->dedup).
- **Auto-tagging**: Rekognition DetectLabels; AEM Enhanced Smart Tags (train on vocabulary). OSS: RAM/RAM++ (Apache, 6,400 categories), avoid AGPL YOLO.
- **Semantic/NL search**: CLIP/OpenCLIP/SigLIP embeddings + pgvector/Qdrant/Milvus. Bynder+AWS Titan = 75% less search time. CLIP weak on fine-grained attributes.
- **Visual similarity**: same embeddings, image as query.
- **OCR**: Cloudinary=Google Vision; Bynder=Rekognition. OSS: Tesseract, PaddleOCR.
- **Face recognition**: detection != identification (legal line). **BIPA** ($1k-5k/violation, Meta paid $650M) + GDPR Art 9. Ship off by default, opt-in, self-host only. Aprimo's anonymous face IDs = privacy-by-design model.
- **Transcription**: Whisper (MIT)/faster-whisper/WhisperX. Lighter privacy risk.
- **Smart cropping**: saliency; smartcrop.js (MIT). Twitter's biased crop removed 2021 -> always ship manual override.
- **Dedup**: perceptual hash (Hamming) + deep embedding cosine. Caution: don't delete intentional brand variants.
- **Auto-descriptions/alt-text**: multimodal LLM captioning (BLIP-2, LLaVA, Qwen2-VL Apache). **Hallucination risk** (wrong alt-text misinforms) -> AI-assisted, human-verified.
- **2024-26 trends**: generative editing in-DAM (Cloudinary), GenAI creation (Adobe Firefly), AI agents/copilots (mandatory human-in-loop), RAG over libraries, multimodal-LLM tagging vs classifier APIs, C2PA provenance.
- **Verdict**: 2026 Forrester Wave leaders Aprimo/Orange Logic/Adobe/Bynder/OpenText (Bynder perfect AI score). OSS: ResourceSpace most AI-complete; Immich cleanest reference architecture (Python ML service + pgvector + Redis jobs).

## 4. Accessibility and compliance
Two distinct obligations: (1) **accessibility of the DAM UI** (WCAG/508/VPAT evaluate this, direct legal exposure), (2) **accessibility of asset content** (alt-text/captions; DAM must manage + propagate, never strip on export).
- **WCAG 2.1/2.2**: AA is the target. 2.2 adds Dragging Movements (non-drag alt for drag-drop upload), Target Size 24x24px, Focus Appearance. **DOJ ADA Title II (2024)** adopts WCAG 2.1 AA for state/local gov; April 2026 IFR extended deadlines to **April 2027** (pop 50k+) / **April 2028** (smaller). Build to **2.2 AA**.
- **Section 508 / EN 301 549 / VPAT**: 508 references WCAG 2.0 AA; build to 2.2 AA to cover all. A filled VPAT = an **ACR**; agencies generally cannot buy ICT without one, so publishing a VPAT is effectively mandatory even for free software.
- **Alt-text/captions/transcripts**: WCAG SC 1.1.1 (Level A), 1.2.x captions. Mechanism: **IPTC Alt Text + Extended Description fields** (embed in XMP, travel with asset). DAM must store as structured fields, require on publish, **never strip on transform**, distribute via API.
- **EAA** (EU 2019/882, in force June 2025): extends accessibility to consumer e-commerce; extraterritorial; WCAG 2.1 AA via EN 301 549.
- **Records retention / legal holds / disposition**: Federal Records Act + NARA GRS; **cannot destroy records without an approved schedule** (44 USC 3314); legal holds hard-block deletion. DAM needs per-asset retention/disposition dates + mandatory-review workflow + legal-hold flag + permanent-record export with fixity.
- **FOIA / public records**: discoverability within deadlines, **non-destructive redaction** (blur exempt portions without destroying original, traceable), audit of searched/released/withheld.
- **Audit / SOC 2 / ISO 27001 / FedRAMP**: append-only queryable audit log of every asset event incl. auth failures, exportable to SIEM. FedRAMP (NIST 800-53) mandatory for federal cloud, higher bar than SOC 2.
- **Privacy (GDPR/CCPA/BIPA)**: GDPR Art 17 erasure across originals/derivatives/backups, yielding to legal hold (hold wins, logged). Face recognition triggers BIPA/GDPR Art 9 -> opt-in, off by default.
- **Hard procurement gates**: WCAG AA UI, 508 VPAT/ACR, FedRAMP (federal SaaS), retention+disposition+legal hold, audit trail, FOIA-ready search + non-destructive redaction.

## 5. Top pain points (synthesized, recurring across independent sources)
1. **Cost: per-seat pricing + opaque quotes** (the loudest complaint; per-seat "discourages adding collaborators," rations the adoption the DAM needs; hidden inflators, $5k-25k onboarding).
2. **Clunky/unintuitive UX, too many clicks** (users revert to old systems; more features worsen adoption).
3. **Search quality** (missing/inconsistent metadata makes assets "practically invisible"; inconsistent terms miss ~75% of relevant assets).
4. **Metadata burden** (uploaded without tagging; AI auto-tags are "generic, technically correct, practically useless," no campaign/channel context; users request ability to delete bad AI tags).
5. **Adoption: people keep using shared drives** (Dropbox/Drive friction-light; folders+links instinctive).
6. **Onboarding/implementation** (six-month projects; over-scoping collapses).
7. **Vendor lock-in** (walled gardens, API-exit refusal "violation of trust"; <1 in 10 buyers check portability).
8. **Performance/scale** (search degrades at 100k-1M+ without indexing; large video).
9. **Integrations** (leaving creative/office apps to download/re-upload kills adoption).
10. **Governance: the stale dumping ground** (fills with duplicates/old assets, no clear owner; over-correction = "Department of No").
11. **The free/OSS gap**: ResourceSpace (dated UI, capped free tier, complex setup), Pimcore (steep learning curve, overkill). **Thin middle of genuinely modern, easy, self-hostable options.**

## 6. Design implications (prioritized)
**Tier 1 (invert the loudest complaints):** no per-seat tax / zero cost; real unrestricted export + API marketed as a feature; search that works without perfect metadata (embed-once-vary-query); clean modern fast UX that beats Dropbox, resist feature bloat.
**Tier 2 (standards + AI moat):** lossless standards-correct metadata (EXIF/IPTC IIM+XMP, Get-Edit-Replace, preserve through every derivative, orientation, sidecars); AI as suggestion + easy human correction never silent replacement (permissive models; layer brand taxonomy on AI tags); authority control by URI; C2PA preserved across edits.
**Tier 3 (gov/GLAM unlock):** WCAG 2.2 AA UI + published VPAT/ACR; compliance primitives (append-only audit, retention/disposition + legal hold, non-destructive redaction, GDPR erasure yielding to holds); interoperate via IIIF + OAI-PMH + Schema.org + METS/MODS/PREMIS/EAD.
**Tier 4 (ops):** performance at scale (proxies, careful dedup, BYOS, tiered storage, large video); in-app integrations (Adobe CC, M365, Workspace, CMS/PIM, webhooks); governance in the workflow not as gatekeeping; stay focused, resist over-scoping.
