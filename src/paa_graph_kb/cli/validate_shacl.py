from __future__ import annotations
import argparse
from pathlib import Path
from rdflib import Graph
from pyshacl import validate

def main() -> None:
    ap = argparse.ArgumentParser(description="Validate a graph against SHACL shapes using pyshacl.")
    ap.add_argument("--data", type=Path, required=True, help="Data TTL/JSON-LD file")
    ap.add_argument("--shapes", type=Path, required=True, help="Shapes TTL file")
    args = ap.parse_args()

    data_g = Graph().parse(args.data, format="turtle")
    shapes_g = Graph().parse(args.shapes, format="turtle")

    conforms, report_graph, report_text = validate(
        data_g, shacl_graph=shapes_g, inference="rdfs", abort_on_first=False, meta_shacl=False, advanced=False
    )
    print(report_text)
    if conforms:
        print("✅ SHACL validation: conforms")
    else:
        print("❌ SHACL validation: violations detected")

if __name__ == "__main__":
    main()
