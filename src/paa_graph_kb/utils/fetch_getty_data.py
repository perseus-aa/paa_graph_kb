"""
Script to fetch and cache Getty JSON-LD records based on reconciled links.

Process:
1. Load the reconciliation graph (perseus_getty_links.ttl).
2. Extract all Getty URIs (objects of owl:sameAs statements).
3. Use GettyClient to fetch and cache these records locally.
"""

import argparse
import logging
from pathlib import Path
from typing import Set

from rdflib import Graph
from rdflib.namespace import OWL

from paa_graph_kb.clients.getty_client import GettyClient

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_getty_uris(reconciliation_path: Path) -> Set[str]:
    """Extract Getty URIs from the reconciliation graph."""
    logger.info(f"Loading reconciliation graph: {reconciliation_path}")
    g = Graph()
    g.parse(reconciliation_path, format="turtle")
    
    uris = set()
    for o in g.objects(predicate=OWL.sameAs):
        uri = str(o)
        if "data.getty.edu" in uri:
            uris.add(uri)
            
    logger.info(f"Found {len(uris)} unique Getty URIs.")
    return uris

def fetch_records(uris: Set[str], cache_dir: Path):
    """Fetch and cache records using GettyClient."""
    client = GettyClient(cache_dir=str(cache_dir))
    
    total = len(uris)
    success = 0
    failed = 0
    
    logger.info(f"Starting fetch for {total} records...")
    
    for i, uri in enumerate(uris):
        try:
            # The client handles caching automatically in _request
            # We just need to trigger the fetch.
            data = client._request(uri)
            if data:
                success += 1
            else:
                failed += 1
                logger.warning(f"Failed to fetch {uri} (Empty response)")
                
        except Exception as e:
            failed += 1
            logger.error(f"Error fetching {uri}: {e}")
            
        if (i + 1) % 10 == 0:
            logger.info(f"Progress: {i + 1}/{total}")

    logger.info(f"Fetch complete. Success: {success}, Failed: {failed}")

def main():
    parser = argparse.ArgumentParser(description="Fetch Getty records from reconciliation links.")
    parser.add_argument(
        "--links", 
        type=Path, 
        default=Path("data/reconciliation/perseus_getty_links.ttl"),
        help="Path to reconciliation TTL file"
    )
    parser.add_argument(
        "--cache-dir", 
        type=Path, 
        default=Path("data/getty/objects"),
        help="Directory to store cached JSON-LD files"
    )
    
    args = parser.parse_args()
    
    uris = load_getty_uris(args.links)
    
    if uris:
        fetch_records(uris, args.cache_dir)
    else:
        logger.warning("No URIs found to fetch.")

if __name__ == "__main__":
    main()
