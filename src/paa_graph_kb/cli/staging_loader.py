from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

from paa_graph_kb.clients.ham_client import HAMClient
from paa_graph_kb.models.ham.models import HAMObject

STG = Namespace("https://aa.perseus.org/staging#")
EXS = Namespace("https://aa.perseus.org/staging/")
AAT = "http://vocab.getty.edu/aat/"


def _safe_lang_literal(text: str) -> Literal:
    # best-effort language tagging
    if text and all(ord(ch) < 128 for ch in text):
        return Literal(text, lang="en")
    return Literal(text)


def object_to_staging(g: Graph, obj: HAMObject, source: str = "ham") -> None:
    sid = f"o/{source}:{obj.objectid}"
    s = EXS[sid]
    g.add((s, RDF.type, STG.Object))
    g.add((s, STG.source, Literal(source)))
    g.add((s, STG.objectid, Literal(obj.objectid, datatype=XSD.integer)))

    # Titles
    if obj.title:
        g.add((s, STG.title, _safe_lang_literal(obj.title)))
    if obj.titles:
        for t in obj.titles:
            if t.title:
                g.add((s, STG.title, _safe_lang_literal(t.title)))

    # Culture (demo)
    if obj.culture and obj.culture.lower() == "greek":
        g.add((s, STG.cultureAAT, URIRef(AAT + "300386130")))

    # Worktypes (demo)
    if obj.worktypes:
        for wt in obj.worktypes:
            low = (wt.worktype or "").lower()
            if "kylix" in low:
                g.add((s, STG.aatType, URIRef(AAT + "300198842")))
            elif "vessel" in low:
                g.add((s, STG.aatType, URIRef(AAT + "300193015")))

    # Materials / techniques (demo)
    if obj.medium and "terracotta" in (obj.medium or "").lower():
        g.add((s, STG.materialAAT, URIRef(AAT + "300265960")))
    if obj.technique and "black glaze" in (obj.technique or "").lower():
        g.add((s, STG.techniqueAAT, URIRef(AAT + "300404385")))

    # Period
    if obj.periodid is not None:
        g.add((s, STG.periodId, Literal(obj.periodid, datatype=XSD.integer)))
    if obj.period:
        g.add((s, STG.periodLabel, _safe_lang_literal(obj.period)))

    # Representations
    if obj.seeAlso:
        for it in obj.seeAlso:
            if it.type and "IIIF" in it.type.upper() and it.id:
                g.add((s, STG.iiifManifest, URIRef(str(it.id))))
    if obj.primaryimageurl:
        g.add((s, STG.primaryImage, URIRef(str(obj.primaryimageurl))))

    # Catalog page
    if obj.url:
        g.add((s, STG.catalogPage, URIRef(str(obj.url))))

    # Notes
    if obj.creditline:
        g.add((s, STG.creditline, Literal(obj.creditline)))
    if obj.provenance:
        g.add((s, STG.provenance, Literal(obj.provenance)))

    # Dimensions
    if obj.dimensions:
        g.add((s, STG.dimensions, Literal(obj.dimensions)))

    # Additional textual descriptions
    if obj.description:
        g.add((s, STG.description, Literal(obj.description)))
    if obj.commentary:
        g.add((s, STG.commentary, Literal(obj.commentary)))
    if obj.labeltext:
        g.add((s, STG.labeltext, Literal(obj.labeltext)))

    # Identifiers
    if obj.objectnumber:
        g.add((s, STG.objectnumber, Literal(obj.objectnumber)))
    if obj.standardreferencenumber:
        g.add((s, STG.standardreferencenumber, Literal(obj.standardreferencenumber)))

    # Dating information
    if obj.datebegin is not None:
        g.add((s, STG.datebegin, Literal(obj.datebegin, datatype=XSD.integer)))
    if obj.dateend is not None:
        g.add((s, STG.dateend, Literal(obj.dateend, datatype=XSD.integer)))
    if obj.dated:
        g.add((s, STG.dated, Literal(obj.dated)))
    if obj.century:
        g.add((s, STG.century, Literal(obj.century)))

    # Classification
    if obj.classification:
        g.add((s, STG.classification, Literal(obj.classification)))
    if obj.style:
        g.add((s, STG.style, Literal(obj.style)))

    # Department/Division
    if obj.department:
        g.add((s, STG.department, Literal(obj.department)))
    if obj.division:
        g.add((s, STG.division, Literal(obj.division)))

    # Colors
    if obj.colors:
        for color in obj.colors:
            if color.color:
                g.add((s, STG.colorName, Literal(color.color)))
                if color.spectrum:
                    # Store hex value as additional property
                    color_bn = URIRef(
                        f"https://aa.perseus.org/staging/color/{obj.objectid}/{color.color}"
                    )
                    g.add((color_bn, STG.hexValue, Literal(color.spectrum)))
                    g.add((s, STG.hasColor, color_bn))

    # Accession information
    if obj.accessionyear is not None:
        g.add((s, STG.accessionyear, Literal(obj.accessionyear, datatype=XSD.integer)))
    if obj.accessionmethod:
        g.add((s, STG.accessionmethod, Literal(obj.accessionmethod)))


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Load HAM objects via the Pydantic client and emit STAGING triples."
    )
    ap.add_argument("--apikey", required=True)
    ap.add_argument("--base", default="https://api.harvardartmuseums.org")
    ap.add_argument(
        "--params",
        nargs="*",
        default=[],
        help="key=value pairs, e.g., culture=Greek hasimage=1",
    )
    ap.add_argument("--size", type=int, default=100)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    # Parse params
    param_dict: dict[str, str] = {}
    for p in args.params:
        if "=" in p:
            k, v = p.split("=", 1)
            param_dict[k] = v
        else:
            param_dict[p] = "1"

    # HAMClient reads from env vars, so set them temporarily if provided via args
    import os
    if args.apikey:
        os.environ['HAM_APIKEY'] = args.apikey
    if args.base:
        os.environ['HAM_API_BASE'] = args.base

    client = HAMClient()
    g = Graph()
    g.bind("stg", STG)
    g.bind("exs", EXS)

    count = 0
    for rec in client.iter_objects(params=param_dict, size=args.size, limit=args.limit):
        object_to_staging(g, rec, source="ham")
        count += 1

    g.serialize(destination=args.out, format="turtle")
    print(f"✅ Wrote {count} objects and {len(g)} staging triples to {args.out}")


if __name__ == "__main__":
    main()
