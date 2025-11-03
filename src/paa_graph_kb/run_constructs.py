#!/usr/bin/env python3
"""Run SPARQL CONSTRUCT templates over a staging graph to produce Linked Art triples.

Usage:
  python run_constructs.py --staging staging.ttl --out linkedart.ttl [--templates templates] [--no-recursive]

Notes:
  - Discovers all *.rq files in the templates directory (recursively by default), sorted lexically.
  - Uses rdflib's SPARQL engine (fine for development). For production, run queries in GraphDB/Jena.
"""

import argparse
from pathlib import Path
from rdflib import Graph

def discover_templates(templates_dir: Path, recursive: bool = True) -> list[Path]:
    if not templates_dir.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
    glober = templates_dir.rglob if recursive else templates_dir.glob
    files = sorted([p for p in glober("*.rq") if p.is_file()])
    if not files:
        raise FileNotFoundError(f"No .rq files found under: {templates_dir}")
    return files

def run(staging_path: Path, templates_dir: Path, out_path: Path, recursive: bool = True) -> None:
    print(f"→ Loading staging graph: {staging_path}")
    g_in = Graph()
    g_in.parse(staging_path, format="turtle")

    g_out = Graph()
    g_out.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
    g_out.bind("la",  "https://linked.art/ns/terms/")
    g_out.bind("rdfs","http://www.w3.org/2000/01/rdf-schema#")

    files = discover_templates(templates_dir, recursive=recursive)
    print(f"→ Found {len(files)} template(s) under {templates_dir} (recursive={recursive})")

    total_added = 0
    for rq in files:
        try:
            qtxt = rq.read_text(encoding="utf-8")
            res = g_in.query(qtxt)  # rdflib returns a Graph for CONSTRUCT
            added = len(res.graph)
            g_out += res.graph
            total_added += added
            print(f"✓ {rq.relative_to(templates_dir)}: +{added} triples")
        except Exception as e:
            print(f"✗ ERROR applying {rq.relative_to(templates_dir)}: {e}")
            raise

    g_out.serialize(destination=out_path, format="turtle")
    print(f"✅ Wrote {len(g_out)} triples to {out_path} (added {total_added} from {len(files)} template(s))")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", type=Path, required=True, help="Path to staging TTL")
    ap.add_argument("--out", type=Path, required=True, help="Output Turtle path")
    ap.add_argument("--templates", type=Path, default=Path("templates"), help="Directory with .rq files (default: ./templates)")
    ap.add_argument("--no-recursive", action="store_true", help="Disable recursive discovery of .rq files")
    args = ap.parse_args()

    run(args.staging, args.templates, args.out, recursive=(not args.no_recursive))

if __name__ == "__main__":
    main()
