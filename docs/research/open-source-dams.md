# Open-Source DAM Landscape (research source)

Compiled June 2026 via live web research. This is the raw, citation-backed
findings file that feeds the synthesized comparison in `RESEARCH.md`.

## A. General-purpose open-source DAMs
- **ResourceSpace** (PHP/MySQL, BSD-style, Montala). Strongest gov/NGO adopter list: WWF, British Red Cross, UNICEF, Oxfam, UK Government, European Commission, NHS. Mature AI: GPT auto-tagging, Tesseract OCR, Whisper STT, InsightFace+FAISS face recognition. Weakness: heavy RAM/deps, UI "less intuitive," thin docs.
- **Piwigo** (PHP/MySQL, GPLv2). Used by Paris 1 Panthéon-Sorbonne, French Ministry of the Interior, American Southwest Virtual Museum. Easy Docker. AI is third-party-API only; no native OCR/face. Image-centric.
- **Razuna** (J2EE/ColdFusion, AGPLv3). OSS edition openly ABANDONED ("no longer maintained"); real product is paid SaaS. Abandonment risk.
- **Pimcore** (PHP/Symfony). DAM is a module of a PIM/MDM suite. License changed off GPL to revenue-gated POCL in 2025.1. Strong Copilot AI. UI "less modern," needs developers.
- **Phraseanet** (PHP/Elasticsearch, GPLv3, Alchemy). City of Paris, France Télévisions, many French city halls. IPTC/XMP/thesaurus, fast ES search. French-centric; admin UI hard; Phrasea successor uncertainty.
- **EnterMedia / eMedia** (Java/Tomcat/ES, LGPL3). Tiny community (~13 stars), rebrand after apparent stall. Complex install.

## B. Museum / heritage collection systems
- **CollectiveAccess** (PHP/MySQL, GPLv3). Heritage heavyweight: Seattle Municipal Archives, White House Historical Assn, 9/11 Memorial, AMNH, Princeton. Ships DACS/Dublin Core/VRA Core; exports EAD + Dublin Core via OAI-PMH; LC + Getty vocabularies; MARC import. NO official Docker; no native AI.
- **Omeka / Omeka S** (PHP, GPLv3, RRCHNM/GMU). Harvard, Yale. Omeka S has JSON-LD REST API + IIIF. Steep learning curve; module bus-factor; Classic stuck on dead Zend 2.
- **Tainacan** (WordPress plugin, GPLv3, Univ. Brasília). 30+ IBRAM museums, Mexico federal gov, Europeana-profiled. REST API. WordPress-bound; no AI.
- **Daminion** (Windows, PROPRIETARY; free Standalone capped at 15k images, single-user). Built-in paid AI tagging + on-prem face recognition. Server edition paid.

## C. Institutional repositories & digital preservation
- **DSpace** (Java/Angular/Solr/Postgres, BSD, LYRASIS). Most-deployed (1,500-3,000+ repos): World Bank OKR, WHO IRIS, MIT, Harvard DASH, Cambridge. OAIS, OAI-PMH, Dublin Core, SWORD, IIIF/Mirador. DSpace 7 Angular rewrite regressed performance + accessibility; 6-8GB RAM. No shipping AI (RAG is roadmap).
- **Islandora** (Drupal+Fedora, GPL). U of Toronto, Grinnell. OAI-PMH + SPARQL + IIIF + MODS/RDF. Ships Tesseract OCR. "Many pieces of software… daunting"; heaviest stack.
- **Fedora Commons** (Java, Apache 2.0, LYRASIS). National Libraries of Ireland/Wales, Slovenia Archives, US NLM, Staatsbibliothek Berlin. Native RDF, LDP, SPARQL, OCFL durable storage. Bare middleware; migration pain.
- **Archivematica** (Python/Django, AGPL3, Artefactual). The OSS standard for national/state archives: City of Vancouver, IMF, Library & Archives Canada, UK National Archives, Wellcome, MoMA. METS/PREMIS/Dublin Core/BagIt AIPs, PRONOM format registry. Brittle microservices; Docker dev-only; no native AI.
- **Nuxeo** (Java, Apache 2.0, acquired by Hyland 2021). UC Libraries. Nuxeo Insight ML (Rekognition/Comprehend/Vision). Openness friction under Hyland; not OAIS preservation.

## D. AI-forward self-hosted photo libraries (strong local AI, weak standards)
- **Immich** (TS/Flutter, AGPL3, ~105k stars). CLIP semantic search + local face recognition. Google Photos clone. NO Dublin Core / OAI-PMH / IIIF / preservation.
- **PhotoPrism** (Go/TensorFlow, AGPL3). Local face + object tagging, Ollama captioning. Multi-user gated behind paid Plus.
- **LibrePhotos** (Django/React, MIT). Face clustering, BLIP/Moondream captioning, places365.
- **digiKam** (KDE, GPL2+). Desktop; deep EXIF/IPTC/XMP, local face + DL auto-tagging. Desktop-only, no multi-user web.
- **Damselfly** (.NET, GPL3). Large IPTC libraries, local offline face/object detection, RBAC.
- Adjacent: AtroDAM, Mayan EDMS (OCR), Cantaloupe (IIIF image server), Lychee, Nextcloud Memories.

## Recurring gaps (the opening)
1. Painful install/ops across the heritage/repository tier (Archivematica, Islandora, DSpace, CollectiveAccess).
2. No official/current production Docker (CollectiveAccess, Omeka, EnterMedia, Archivematica = dev-only).
3. Dated UI / failed accessibility audits (Pimcore, Daminion, DSpace 7 regression).
4. Weak/slow search at scale (Daminion, Omeka S, DSpace 7 high-CPU).
5. AI absent, bolted-on, or paywalled in the standards-rich tier.
6. **THE BIG ONE: no OSS tool marries archival metadata standards (Dublin Core, METS, PREMIS, EAD, OAI-PMH, IIIF) with modern local AI and a clean UI.** Heritage tools have standards but no AI/UX; photo libraries have AI/UX but no standards. The intersection is empty.
7. Bus-factor / abandonment risk (Razuna abandoned, EnterMedia stalled, Omeka module single-author, Pimcore license shift, Nuxeo governance).
8. Thin or awkward APIs (CollectiveAccess, EnterMedia, older Omeka).
