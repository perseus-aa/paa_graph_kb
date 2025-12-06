"""
Script to identify Perseus objects belonging to Harvard Art Museums,
fetch their full records from the HAM API, and cache them locally.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Set

from rdflib import Graph, Namespace

from paa_graph_kb.clients.ham_client import HAMClient

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

STG = Namespace("https://aa.perseus.org/staging#")

def load_perseus_candidates(staging_path: Path) -> Dict[str, str]:
    """
    Load Perseus staging data and return a dict of {accession_number: perseus_uri}
    for objects belonging to Harvard Art Museums.
    """
    logger.info(f"Loading Perseus staging data from {staging_path}...")
    g = Graph()
    g.parse(staging_path, format="turtle")
    
    candidates = {}
    
    # Iterate over all objects with institution "Harvard Art Museums"
    for s in g.subjects(predicate=STG.institution):
        inst_name = str(g.value(s, STG.institution))
        if "Harvard" in inst_name:
            acc_num = g.value(s, STG.accessionNumber)
            if acc_num:
                # Clean accession number
                acc = str(acc_num).strip()
                candidates[acc] = str(s)
                
    logger.info(f"Found {len(candidates)} HAM candidates in Perseus staging.")
    return candidates

def fetch_and_cache_records(accession_numbers: List[str], cache_dir: Path):
    """
    Search HAM API for each accession number and cache the result.
    """
    client = HAMClient(cache_dir=str(cache_dir))
    
    found = 0
    missing = 0
    total = len(accession_numbers)
    
    logger.info(f"Searching HAM API for {total} accession numbers...")
    
    for i, acc in enumerate(accession_numbers):
        try:
            # Check if we already have it in cache (HAMClient handles this somewhat, 
            # but searching by accession number is query-based, so cache might strictly be by ID.
            # We'll rely on the search.)
            
            # Search for object by objectnumber
            # Using 'strict=True' to iterate might imply paging, but here we expect 1 result.
            # The HAM API allows searching by 'objectnumber'.
            
            results = list(client.iter_objects(params={"objectnumber": acc}, limit=1))
            
            if results:
                obj = results[0]
                # The client automatically caches the individual object record when it fetches details 
                # if we iterate. Wait, client.iter_objects calls _iter_model which calls _fetch_page.
                # It doesn't necessarily fetch/cache the individual object detail endpoint unless needed?
                # 
                # Let's look at HAMClient: 
                # It iterates over pages. The pages contain records.
                # It doesn't seem to explicitly cache individual object JSONs by ID in `cache_dir` 
                # unless `_request` is called for that specific ID.
                #
                # However, `HAMClient` inherits from `Client`.
                # If we want to ensure the full record is cached by ID (for later loading),
                # we should verify if the search result is the full record or a summary.
                # HAM API search results are usually robust.
                #
                # Let's ensure we save it to our expected file structure: `cache_dir / {hash}.json`
                # or `cache_dir / {id}.json`.
                
                # Manually save the record to ensure it's in the cache dir we expect for the loader
                save_path = cache_dir / f"{obj.id}.json"
                if not save_path.exists():
                    with open(save_path, "w", encoding="utf-8") as f:
                        # obj is a Pydantic model, convert back to dict
                        json.dump(obj.model_dump(mode='json'), f, indent=2)
                    logger.info(f"[{i+1}/{total}] Found & Cached: {acc} -> {obj.id}")
                else:
                    logger.info(f"[{i+1}/{total}] Found (Already Cached): {acc} -> {obj.id}")
                
                found += 1
            else:
                logger.warning(f"[{i+1}/{total}] Not Found: {acc}")
                missing += 1
                
        except Exception as e:
            logger.error(f"[{i+1}/{total}] Error fetching {acc}: {e}")
            missing += 1

    logger.info(f"Fetch complete. Found: {found}, Missing: {missing}")

def main():
    parser = argparse.ArgumentParser(description="Fetch HAM records for Perseus objects.")
    parser.add_argument(
        "--input", 
        type=Path, 
        default=Path("data/staging/perseus_objects.ttl"),
        help="Path to Perseus staging turtle file"
    )
    parser.add_argument(
        "--cache-dir", 
        type=Path, 
        default=Path("data/ham/objects"),
        help="Directory to store cached JSON files"
    )
    
    args = parser.parse_args()
    
    # 1. Load candidates
    candidates = load_perseus_candidates(args.input)
    if not candidates:
        logger.warning("No candidates found. Exiting.")
        sys.exit(0)
    
    # 2. Create cache dir
    args.cache_dir.mkdir(parents=True, exist_ok=True)
        
    # 3. Fetch records
    accession_numbers = list(candidates.keys())
    fetch_and_cache_records(accession_numbers, args.cache_dir)

if __name__ == "__main__":
    main()
