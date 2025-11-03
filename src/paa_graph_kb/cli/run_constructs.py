from __future__ import annotations
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

def main() -> None:
    ap = argparse.ArgumentParser(description="Run SPARQL CONSTRUCT templates over a staging graph to produce Linked Art triples.")
    ap.add_argument("--staging", type=Path, required=True, help="Path to staging TTL")
    ap.add_argument("--out", type=Path, required=True, help="Output Turtle path")
    ap.add_argument("--templates", type=Path, default=Path("templates"), help="Directory with .rq files (default: ./templates)")
    ap.add_argument("--no-recursive", action="store_true", help="Disable recursive discovery of .rq files")
    args = ap.parse_args()

    print(f"→ Loading staging graph: {args.staging}")
    g_in = Graph()
    g_in.parse(args.staging, format="turtle")

    g_out = Graph()
    g_out.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
    g_out.bind("la",  "https://linked.art/ns/terms/")
    g_out.bind("rdfs","http://www.w3.org/2000/01/rdf-schema#")

    files = discover_templates(args.templates, recursive=(not args.no_recursive))
    print(f"→ Found {len(files)} template(s) under {args.templates} (recursive={not args.no_recursive})")

    total_added = 0
    for rq in files:
        try:
            qtxt = rq.read_text(encoding="utf-8")
            res = g_in.query(qtxt)  # rdflib returns a Graph for CONSTRUCT
            added = len(res.graph)
            g_out += res.graph
            total_added += added
            print(f"✓ {rq.relative_to(args.templates)}: +{added} triples")
        except Exception as e:
            print(f"✗ ERROR applying {rq.relative_to(args.templates)}: {e}")
            raise

    g_out.serialize(destination=args.out, format="turtle")
    print(f"✅ Wrote {len(g_out)} triples to {args.out} (added {total_added} from {len(files)} template(s))")

if __name__ == "__main__":
    main()
