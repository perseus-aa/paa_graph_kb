"""
Script to reconcile Perseus objects with Getty Museum records.

Process:
1. Load Perseus staging graph.
2. Filter for objects where stg:institution is "J. Paul Getty Museum".
3. Extract accession numbers.
4. Batch query the Getty SPARQL endpoint to find matching Getty URIs.
5. Generate an owl:sameAs mapping file.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, JSON

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

STG = Namespace("https://aa.perseus.org/staging#")

GETTY_SPARQL_ENDPOINT = "https://data.getty.edu/museum/collection/sparql"

def load_perseus_candidates(staging_path: Path) -> Dict[str, URIRef]:
    """
    Load Perseus staging data and return a dict of {accession_number: perseus_uri}
    for objects belonging to the Getty Museum.
    """
    logger.info(f"Loading Perseus staging data from {staging_path}...")
    g = Graph()
    g.parse(staging_path, format="turtle")
    
    candidates = {}
    
    # Iterate over all objects with institution "J. Paul Getty Museum"
    # Note: We might need to be flexible with the institution string matching
    for s in g.subjects(predicate=STG.institution):
        inst_name = str(g.value(s, STG.institution))
        if "Getty" in inst_name:
            acc_num = g.value(s, STG.accessionNumber)
            if acc_num:
                # Clean accession number (strip whitespace)
                acc = str(acc_num).strip()
                candidates[acc] = s
                
    logger.info(f"Found {len(candidates)} Getty candidates in Perseus staging.")
    return candidates

def batch_query_getty(accession_numbers: List[str], batch_size: int = 50) -> Dict[str, str]:
    """
    Query Getty SPARQL endpoint to find URIs for the given list of accession numbers.
    Returns a dict of {accession_number: getty_uri}.
    """
    matches = {}
    total = len(accession_numbers)
    sparql = SPARQLWrapper(GETTY_SPARQL_ENDPOINT)
    sparql.setReturnFormat(JSON)

    for i in range(0, total, batch_size):
        batch = accession_numbers[i : i + batch_size]
        logger.info(f"Querying batch {i//batch_size + 1} ({len(batch)} items)...")
        
        # Escape strings for SPARQL
        values_str = " ".join([f'"{acc}"' for acc in batch])
        
        # Query explanation:
        # ?o is the Object
        # ?id is the Identifier object
        # ?id_value is the literal accession number
        # We look for identifiers that match our list.
        # CRM: E22_Human-Made_Object P1_is_identified_by E42_Identifier
        # E42_Identifier P190_has_symbolic_content "Literal Value"
        query = f"""
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?acc ?obj WHERE {{
            VALUES ?acc {{ {values_str} }}
            
            ?obj a crm:E22_Human-Made_Object ;
                 crm:P1_is_identified_by ?id_resource .
            
            ?id_resource crm:P190_has_symbolic_content ?acc .
        }}
        """
        
        sparql.setQuery(query)
        
        try:
            results = sparql.query().convert()
            for row in results["results"]["bindings"]:
                acc = row["acc"]["value"]
                uri = row["obj"]["value"]
                matches[acc] = uri
        except Exception as e:
            logger.error(f"Error querying batch: {e}")
            
    return matches

def generate_reconciliation_graph(
    matches: Dict[str, str], 
    candidates: Dict[str, URIRef]
) -> Graph:
    """
    Generate an RDF graph linking Perseus URIs to Getty URIs using owl:sameAs.
    """
    g = Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    
    # We need to reconstruct the CRM URI for the Perseus object locally 
    # OR we can just link the staging URI?
    #
    # The current HAM reconciliation script links:
    #   <http://aa.perseus.org/id/thing/{hash}> owl:sameAs <http://aa.perseus.org/id/thing/{hash}>
    #   Wait, the HAM script calculates the hash for *both* and links them.
    #   
    #   Ideally, we want to link the Perseus Entity (UUID-based) to the Getty Entity (URI).
    #   Since we don't have the final UUIDs in the staging graph easily accessible without hashing,
    #   we will follow the pattern of `entity_resolution.py` which computes the hash from the staging ID.
    
    BASE = "https://aa.perseus.org/id/thing/"
    
    count = 0
    for acc, getty_uri in matches.items():
        if acc in candidates:
            perseus_staging_uri = candidates[acc]
            
            # Generate the Perseus UUID hash
            # Staging URI format: https://aa.perseus.org/staging/o/perseus:aa_123
            if "/o/" in str(perseus_staging_uri):
                staging_id = str(perseus_staging_uri).split("/o/")[1]
                import hashlib
                hash_value = hashlib.sha256(staging_id.encode()).hexdigest()
                perseus_crm_uri = URIRef(BASE + hash_value)
                
                # Getty URI is direct
                getty_crm_uri = URIRef(getty_uri)
                
                g.add((perseus_crm_uri, OWL.sameAs, getty_crm_uri))
                
                # Metadata
                g.add((perseus_crm_uri, RDFS.comment, Literal(f"Perseus Accession: {acc}")))
                count += 1
                
    logger.info(f"Generated {count} links.")
    return g

def main():
    parser = argparse.ArgumentParser(description="Reconcile Perseus Getty objects.")
    parser.add_argument(
        "--input", 
        type=Path, 
        default=Path("data/staging/perseus_objects.ttl"),
        help="Path to Perseus staging turtle file"
    )
    parser.add_argument(
        "--output", 
        type=Path, 
        default=Path("data/reconciliation/perseus_getty_links.ttl"),
        help="Output path for reconciliation graph"
    )
    
    args = parser.parse_args()
    
    # 1. Load candidates
    candidates = load_perseus_candidates(args.input)
    if not candidates:
        logger.warning("No candidates found. Exiting.")
        sys.exit(0)
        
    # 2. Query Getty
    accession_numbers = list(candidates.keys())
    matches = batch_query_getty(accession_numbers)
    
    logger.info(f"Successfully matched {len(matches)} out of {len(candidates)} objects.")
    
    # 3. Generate Graph
    g = generate_reconciliation_graph(matches, candidates)
    
    # 4. Save
    args.output.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=args.output, format="turtle")
    logger.info(f"Saved reconciliation graph to {args.output}")

if __name__ == "__main__":
    main()
