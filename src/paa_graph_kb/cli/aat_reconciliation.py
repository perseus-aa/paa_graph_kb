#!/usr/bin/env python3
"""
Getty AAT Reconciliation Tool

Queries the Getty Art & Architecture Thesaurus (AAT) SPARQL endpoint
to find matching concepts for techniques, object types, and other terms.
"""

import argparse
import json
import time
from typing import List, Dict, Optional
from urllib.parse import quote
import requests


class AATReconciler:
    """Reconciles terms with Getty AAT using SPARQL queries."""

    SPARQL_ENDPOINT = "https://vocab.getty.edu/sparql"

    # SPARQL prefixes
    PREFIXES = """
    PREFIX aat: <http://vocab.getty.edu/aat/>
    PREFIX gvp: <http://vocab.getty.edu/ontology#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX luc: <http://www.ontotext.com/owlim/lucene#>
    PREFIX xl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX dct: <http://purl.org/dc/terms/>
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/sparql-results+json',
            'User-Agent': 'PAA-Graph-KB-Reconciliation/1.0'
        })

    def search_aat(self, term: str, limit: int = 5) -> List[Dict]:
        """
        Search Getty AAT for a term using full-text search.

        Args:
            term: The search term (e.g., "struck", "vessels")
            limit: Maximum number of results to return

        Returns:
            List of dictionaries with keys: uri, prefLabel, scopeNote, type
        """
        # Clean the term for search
        search_term = term.strip().replace('-', ' ')

        query = f"""{self.PREFIXES}

        SELECT DISTINCT ?concept ?prefLabel ?scopeNote ?type
        WHERE {{
          # Full-text search on the term
          ?concept luc:term "{search_term}*" ;
                   skos:inScheme aat: ;
                   gvp:prefLabelGVP/xl:literalForm ?prefLabel .

          # Get the concept type (facet)
          OPTIONAL {{ ?concept gvp:broaderPreferred ?broader .
                      ?broader skos:inScheme aat: . }}

          # Get scope note if available
          OPTIONAL {{ ?concept skos:scopeNote/rdf:value ?scopeNote }}

          # Determine type
          BIND(
            IF(CONTAINS(STR(?concept), "/Activities"), "technique",
            IF(CONTAINS(STR(?concept), "/Objects"), "object_type",
            IF(CONTAINS(STR(?concept), "/Materials"), "material",
            "other"))) AS ?type
          )

          # Prefer exact matches
          FILTER(
            LCASE(?prefLabel) = LCASE("{search_term}") ||
            CONTAINS(LCASE(?prefLabel), LCASE("{search_term}"))
          )
        }}
        ORDER BY
          # Exact matches first
          (LCASE(?prefLabel) = LCASE("{search_term}")) DESC,
          # Then partial matches
          ?prefLabel
        LIMIT {limit}
        """

        if self.verbose:
            print(f"Searching AAT for: {term}")
            print(f"Query: {query[:200]}...")

        try:
            response = self.session.post(
                self.SPARQL_ENDPOINT,
                data={'query': query},
                timeout=30
            )
            response.raise_for_status()

            results = response.json()
            matches = []

            for binding in results.get('results', {}).get('bindings', []):
                matches.append({
                    'uri': binding['concept']['value'],
                    'aat_id': binding['concept']['value'].split('/')[-1],
                    'prefLabel': binding['prefLabel']['value'],
                    'scopeNote': binding.get('scopeNote', {}).get('value', ''),
                    'type': binding.get('type', {}).get('value', 'unknown')
                })

            if self.verbose:
                print(f"  Found {len(matches)} matches")

            return matches

        except requests.exceptions.RequestException as e:
            print(f"Error querying AAT for '{term}': {e}")
            return []

    def reconcile_terms(self, terms: List[str], category: str = "unknown") -> Dict:
        """
        Reconcile a list of terms with Getty AAT.

        Args:
            terms: List of terms to reconcile
            category: Category of terms (e.g., "technique", "object_type")

        Returns:
            Dictionary mapping each term to its AAT matches
        """
        reconciliation = {}

        for i, term in enumerate(terms, 1):
            print(f"[{i}/{len(terms)}] Reconciling: {term}")

            matches = self.search_aat(term)
            reconciliation[term] = {
                'category': category,
                'matches': matches,
                'top_match': matches[0] if matches else None
            }

            # Show top match
            if matches:
                top = matches[0]
                print(f"  → Top match: {top['prefLabel']} ({top['aat_id']})")
                if top['scopeNote']:
                    print(f"     {top['scopeNote'][:100]}...")
            else:
                print(f"  → No matches found")

            # Rate limiting - be nice to Getty's server
            time.sleep(0.5)

        return reconciliation

    def save_mappings(self, reconciliation: Dict, output_file: str):
        """Save reconciliation results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(reconciliation, f, indent=2)
        print(f"\nSaved reconciliation to: {output_file}")

    def generate_mapping_file(self, reconciliation: Dict, output_file: str):
        """
        Generate a simple term→URI mapping file for use in templates.

        Format:
        # Techniques to Getty AAT URIs
        struck: aat:300053140
        red-figure: aat:300020301
        """
        with open(output_file, 'w') as f:
            f.write("# Getty AAT Reconciliation Mappings\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for term, data in sorted(reconciliation.items()):
                category = data.get('category', 'unknown')
                top_match = data.get('top_match')

                if top_match:
                    aat_id = top_match['aat_id']
                    label = top_match['prefLabel']
                    f.write(f"# {term} → {label}\n")
                    f.write(f"{term.lower()}: aat:{aat_id}\n\n")
                else:
                    f.write(f"# {term} → NO MATCH FOUND\n")
                    f.write(f"# {term.lower()}: ???\n\n")

        print(f"Generated mapping file: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Reconcile terms with Getty AAT'
    )
    parser.add_argument(
        '--terms',
        nargs='+',
        help='Terms to reconcile (space-separated)'
    )
    parser.add_argument(
        '--terms-file',
        help='File containing terms (one per line)'
    )
    parser.add_argument(
        '--category',
        default='unknown',
        help='Category of terms (technique, object_type, etc.)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output JSON file for full reconciliation results'
    )
    parser.add_argument(
        '--mapping-file',
        help='Output simple mapping file (term: aat:ID format)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Get terms from command line or file
    if args.terms:
        terms = args.terms
    elif args.terms_file:
        with open(args.terms_file) as f:
            terms = [line.strip() for line in f if line.strip()]
    else:
        parser.error("Either --terms or --terms-file is required")

    # Reconcile
    reconciler = AATReconciler(verbose=args.verbose)
    reconciliation = reconciler.reconcile_terms(terms, category=args.category)

    # Save results
    reconciler.save_mappings(reconciliation, args.output)

    # Generate simple mapping file if requested
    if args.mapping_file:
        reconciler.generate_mapping_file(reconciliation, args.mapping_file)

    # Summary
    total = len(reconciliation)
    matched = sum(1 for data in reconciliation.values() if data.get('top_match'))
    print(f"\n{'='*60}")
    print(f"Reconciliation Summary:")
    print(f"  Total terms: {total}")
    print(f"  Matched: {matched} ({matched/total*100:.1f}%)")
    print(f"  Unmatched: {total - matched}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
