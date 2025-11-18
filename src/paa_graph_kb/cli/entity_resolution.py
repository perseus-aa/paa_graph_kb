"""
Entity resolution for linking Perseus and HAM objects.

This script identifies when Perseus objects and HAM objects refer to the same
physical artifact, and generates owl:sameAs statements to link them.

Matching strategy:
- Match Perseus objects with institution="Harvard Art Museums" to HAM objects
  by comparing accession numbers (stg:accessionNumber == stg:objectnumber)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Set, Tuple

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS

STG = Namespace("https://aa.perseus.org/staging#")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


def load_staging_data(perseus_path: Path, ham_path: Path) -> Tuple[Graph, Graph]:
    """Load Perseus and HAM staging graphs."""
    print(f"📖 Loading Perseus staging: {perseus_path}")
    perseus_g = Graph()
    perseus_g.parse(perseus_path, format="turtle")
    print(f"   Loaded {len(perseus_g)} triples")

    print(f"📖 Loading HAM staging: {ham_path}")
    ham_g = Graph()
    ham_g.parse(ham_path, format="turtle")
    print(f"   Loaded {len(ham_g)} triples")

    return perseus_g, ham_g


def find_matches_by_accession(
    perseus_g: Graph, ham_g: Graph
) -> Dict[str, Tuple[URIRef, URIRef]]:
    """
    Find matches between Perseus and HAM objects by accession number.

    Returns:
        Dictionary mapping accession number to (perseus_uri, ham_uri) tuple
    """
    # Build Perseus Harvard accession number index
    perseus_harvard = {}
    for s in perseus_g.subjects(predicate=STG.institution):
        inst = str(perseus_g.value(s, STG.institution))
        if "Harvard" in inst:
            acc = perseus_g.value(s, STG.accessionNumber)
            if acc:
                perseus_harvard[str(acc)] = s

    # Build HAM object number index
    ham_objects = {}
    for s in ham_g.subjects(predicate=STG.objectnumber):
        objnum = str(ham_g.value(s, STG.objectnumber))
        ham_objects[objnum] = s

    # Find matches
    matches = {}
    for acc, perseus_uri in perseus_harvard.items():
        if acc in ham_objects:
            matches[acc] = (perseus_uri, ham_objects[acc])

    return matches


def generate_hash_from_staging_uri(staging_uri: str) -> str:
    """
    Extract the hash from a staging URI.

    Staging URIs have format: https://aa.perseus.org/staging/o/{source}:{id}
    We need to get the source and id to compute the same hash used in CRM generation.
    """
    import hashlib

    # Extract the staging identifier from the URI
    if "/o/" in staging_uri:
        staging_id = staging_uri.split("/o/")[1]
        # staging_id is like "perseus:aa_123" or "ham:456"
        # The CRM URI uses SHA256(source:id)
        hash_value = hashlib.sha256(staging_id.encode()).hexdigest()
        return hash_value
    return None


def generate_equivalence_graph(
    matches: Dict[str, Tuple[URIRef, URIRef]], perseus_g: Graph, ham_g: Graph
) -> Graph:
    """
    Generate a graph with owl:sameAs statements linking matched entities.

    Args:
        matches: Dictionary mapping accession numbers to (perseus_staging_uri, ham_staging_uri)
        perseus_g: Perseus staging graph
        ham_g: HAM staging graph

    Returns:
        Graph containing equivalence statements
    """
    g = Graph()
    g.bind("owl", OWL)
    g.bind("crm", CRM)
    g.bind("rdfs", RDFS)

    BASE = "https://aa.perseus.org/id/thing/"

    for acc, (perseus_staging_uri, ham_staging_uri) in matches.items():
        # Generate the CRM URIs for both entities
        perseus_hash = generate_hash_from_staging_uri(str(perseus_staging_uri))
        ham_hash = generate_hash_from_staging_uri(str(ham_staging_uri))

        if perseus_hash and ham_hash:
            perseus_crm_uri = URIRef(BASE + perseus_hash)
            ham_crm_uri = URIRef(BASE + ham_hash)

            # Add owl:sameAs statement
            g.add((perseus_crm_uri, OWL.sameAs, ham_crm_uri))
            g.add((ham_crm_uri, OWL.sameAs, perseus_crm_uri))

            # Add rdfs:comment explaining the match
            g.add(
                (
                    perseus_crm_uri,
                    RDFS.comment,
                    Literal(f"Matched to HAM object by accession number: {acc}"),
                )
            )
            g.add(
                (
                    ham_crm_uri,
                    RDFS.comment,
                    Literal(f"Matched to Perseus object by accession number: {acc}"),
                )
            )

    return g


def main() -> None:
    """Main entry point for entity resolution."""
    ap = argparse.ArgumentParser(
        description="Resolve entities between Perseus and HAM datasets by matching accession numbers."
    )
    ap.add_argument(
        "--perseus-staging",
        type=Path,
        required=True,
        help="Path to Perseus staging TTL file",
    )
    ap.add_argument(
        "--ham-staging",
        type=Path,
        required=True,
        help="Path to HAM staging TTL file",
    )
    ap.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output path for equivalence statements TTL",
    )

    args = ap.parse_args()

    # Load staging data
    perseus_g, ham_g = load_staging_data(args.perseus_staging, args.ham_staging)

    # Find matches
    print("\n🔍 Finding matches by accession number...")
    matches = find_matches_by_accession(perseus_g, ham_g)
    print(f"✅ Found {len(matches)} matches")

    if matches:
        print("\n📝 Sample matches:")
        for i, (acc, (p_uri, h_uri)) in enumerate(list(matches.items())[:5]):
            print(f"   {acc}")
            print(f"     Perseus: {p_uri}")
            print(f"     HAM:     {h_uri}")
            if i >= 4:
                break

    # Generate equivalence graph
    print(f"\n🔗 Generating owl:sameAs statements...")
    equiv_g = generate_equivalence_graph(matches, perseus_g, ham_g)
    print(f"   Generated {len(equiv_g)} triples")

    # Write output
    equiv_g.serialize(destination=args.out, format="turtle")
    print(f"\n✅ Wrote equivalence statements to {args.out}")
    print(f"   {len(matches)} entity pairs linked")


if __name__ == "__main__":
    main()
