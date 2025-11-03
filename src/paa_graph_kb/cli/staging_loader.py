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

    client = HAMClient(apikey=args.apikey, base=args.base)
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
