"""Open metadata interoperability standards.

These are the endpoints that separate a serious archival/government DAM
from a glorified file share:

  * Dublin Core (oai_dc)  - the lingua franca of descriptive metadata
  * OAI-PMH               - lets aggregators/harvesters mirror the catalog
  * IIIF Image API        - standard, deep-zoomable, interoperable image URLs

Implemented from the specs on the standard library so there is nothing
extra to install.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from xml.sax.saxutils import escape

from .audit import now_iso
from .config import config
from .db import get_conn


# ---------------------------------------------------------------------------
# Dublin Core
# ---------------------------------------------------------------------------
def dublin_core(asset: dict) -> dict:
    """Map an Keepstack asset onto the 15 Dublin Core elements."""
    return {
        "title": asset.get("title") or asset.get("filename"),
        "creator": asset.get("dc_creator") or asset.get("credit"),
        "subject": asset.get("dc_subject"),
        "description": asset.get("description"),
        "publisher": asset.get("dc_publisher"),
        "date": asset.get("dc_date") or asset.get("created_at"),
        "type": asset.get("media_type"),
        "format": asset.get("mime_type"),
        "identifier": asset.get("uuid"),
        "rights": asset.get("rights_statement") or asset.get("license"),
    }


def _dc_xml_body(asset: dict) -> str:
    dc = dublin_core(asset)
    rows = []
    for term, value in dc.items():
        if value:
            rows.append(f"    <dc:{term}>{escape(str(value))}</dc:{term}>")
    inner = "\n".join(rows)
    return (
        '  <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ '
        'http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n'
        f"{inner}\n  </oai_dc:dc>"
    )


# ---------------------------------------------------------------------------
# OAI-PMH 2.0
# ---------------------------------------------------------------------------
def _oai_header(asset: dict) -> str:
    deleted = ' status="deleted"' if asset.get("status") == "deleted" else ""
    return (
        f'   <header{deleted}>\n'
        f'    <identifier>oai:{_domain()}:{asset["uuid"]}</identifier>\n'
        f'    <datestamp>{_oai_date(asset.get("updated_at"))}</datestamp>\n'
        f'   </header>'
    )


def _domain() -> str:
    return config.base_url.replace("https://", "").replace("http://", "").split("/")[0]


def _oai_date(value: Optional[str]) -> str:
    if not value:
        value = now_iso()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        dt = datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _envelope(verb_body: str, request_attrs: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ '
        'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n'
        f' <responseDate>{_oai_date(None)}</responseDate>\n'
        f' <request {request_attrs}>{escape(config.base_url)}/oai</request>\n'
        f'{verb_body}\n'
        '</OAI-PMH>'
    )


def _error(code: str, message: str) -> str:
    return _envelope(f' <error code="{code}">{escape(message)}</error>', 'verb=""')


def oai_response(params: dict) -> tuple[str, int]:
    verb = params.get("verb", "")
    conn = get_conn()

    if verb == "Identify":
        body = (
            " <Identify>\n"
            f"  <repositoryName>{escape(config.repository_name)}</repositoryName>\n"
            f"  <baseURL>{escape(config.base_url)}/oai</baseURL>\n"
            "  <protocolVersion>2.0</protocolVersion>\n"
            f"  <adminEmail>{escape(config.admin_email)}</adminEmail>\n"
            "  <earliestDatestamp>2020-01-01T00:00:00Z</earliestDatestamp>\n"
            "  <deletedRecord>persistent</deletedRecord>\n"
            "  <granularity>YYYY-MM-DDThh:mm:ssZ</granularity>\n"
            " </Identify>"
        )
        return _envelope(body, 'verb="Identify"'), 200

    if verb == "ListMetadataFormats":
        body = (
            " <ListMetadataFormats>\n"
            "  <metadataFormat>\n"
            "   <metadataPrefix>oai_dc</metadataPrefix>\n"
            "   <schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema>\n"
            "   <metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>\n"
            "  </metadataFormat>\n"
            " </ListMetadataFormats>"
        )
        return _envelope(body, 'verb="ListMetadataFormats"'), 200

    if verb in ("ListRecords", "ListIdentifiers"):
        prefix = params.get("metadataPrefix", "oai_dc")
        if prefix != "oai_dc":
            return _error("cannotDisseminateFormat", "Only oai_dc is supported"), 200
        rows = conn.execute(
            "SELECT * FROM assets WHERE status != 'deleted' ORDER BY id LIMIT 200"
        ).fetchall()
        if not rows:
            return _error("noRecordsMatch", "No records"), 200
        items = []
        for row in rows:
            asset = dict(row)
            if verb == "ListIdentifiers":
                items.append(_oai_header(asset))
            else:
                items.append(
                    f"  <record>\n{_oai_header(asset)}\n   <metadata>\n"
                    f"{_dc_xml_body(asset)}\n   </metadata>\n  </record>"
                )
        wrapper = "ListRecords" if verb == "ListRecords" else "ListIdentifiers"
        body = f" <{wrapper}>\n" + "\n".join(items) + f"\n </{wrapper}>"
        return _envelope(body, f'verb="{verb}" metadataPrefix="oai_dc"'), 200

    if verb == "GetRecord":
        ident = params.get("identifier", "")
        uuid = ident.split(":")[-1]
        row = conn.execute("SELECT * FROM assets WHERE uuid = ?", (uuid,)).fetchone()
        if not row:
            return _error("idDoesNotExist", "Unknown identifier"), 200
        asset = dict(row)
        body = (
            " <GetRecord>\n  <record>\n"
            f"{_oai_header(asset)}\n   <metadata>\n{_dc_xml_body(asset)}\n   </metadata>\n"
            "  </record>\n </GetRecord>"
        )
        return _envelope(body, 'verb="GetRecord" metadataPrefix="oai_dc"'), 200

    return _error("badVerb", "Illegal or missing verb"), 200


# ---------------------------------------------------------------------------
# IIIF Image API 3.0 (info.json)
# ---------------------------------------------------------------------------
def iiif_info(asset: dict) -> dict:
    base = f"{config.base_url}/iiif/3/{asset['uuid']}"
    width = asset.get("width") or 1024
    height = asset.get("height") or 1024
    return {
        "@context": "http://iiif.io/api/image/3/context.json",
        "id": base,
        "type": "ImageService3",
        "protocol": "http://iiif.io/api/image",
        "profile": "level2",
        "width": width,
        "height": height,
        "tiles": [{"width": 512, "scaleFactors": [1, 2, 4, 8, 16]}],
        "sizes": [
            {"width": 256, "height": max(1, round(256 * height / width))},
            {"width": 512, "height": max(1, round(512 * height / width))},
            {"width": 1024, "height": max(1, round(1024 * height / width))},
        ],
        "extraFormats": ["jpg"],
        "extraQualities": ["default"],
    }
