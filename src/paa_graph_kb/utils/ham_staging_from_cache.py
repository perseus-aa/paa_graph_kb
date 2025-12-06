"""
Script to load cached HAM JSON objects and convert them to staging RDF triples.
This bypasses the API client's search/fetch logic and uses local files directly.
"""

import argparse
import json
import logging
from pathlib import Path

from rdflib import Graph, Namespace

from paa_graph_kb.models.ham.models import HAMObject
from paa_graph_kb.cli.staging_loader import object_to_staging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

STG = Namespace("https://aa.perseus.org/staging#")
EXS = Namespace("https://aa.perseus.org/staging/")

def main():
    parser = argparse.ArgumentParser(description="Convert cached HAM JSONs to staging RDF.")
    parser.add_argument(
        "--cache-dir", 
        type=Path, 
        default=Path("data/ham/objects"),
        help="Directory containing cached HAM JSON files"
    )
    parser.add_argument(
        "--out", 
        type=Path, 
        default=Path("data/staging/ham_staging.ttl"),
        help="Output path for staging TTL file"
    )
    
    args = parser.parse_args()
    
    if not args.cache_dir.exists():
        logger.error(f"Cache directory not found: {args.cache_dir}")
        return

    g = Graph()
    g.bind("stg", STG)
    g.bind("exs", EXS)
    
    files = list(args.cache_dir.glob("*.json"))
    logger.info(f"Found {len(files)} JSON files in {args.cache_dir}")
    
    count = 0
    errors = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle raw HAMPage cache files (wrapped in info/records)
            if "records" in data and isinstance(data["records"], list):
                # Process all records in the page (usually 1 if cached by search, but could be more)
                for record in data["records"]:
                    try:
                        obj = HAMObject(**record)
                        object_to_staging(g, obj, source="ham")
                        count += 1
                    except Exception as rec_err:
                        logger.warning(f"Skipping invalid record in {file_path.name}: {rec_err}")
                        errors += 1
                continue # Done with this file

            # Validate with Pydantic model (flat object)
            # The JSON from HAM API usually wraps the object in fields, or is the object itself?
            # HAMClient.iter_objects usually yields HAMObject.
            # The fetch script saved `obj.model_dump(mode='json')`, so it should be the flat object dict.
            
            obj = HAMObject(**data)
            
            object_to_staging(g, obj, source="ham")
            count += 1
            
            if count % 50 == 0:
                logger.info(f"Processed {count} objects...")
                
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            errors += 1
            
    logger.info(f"Conversion complete. Processed: {count}, Errors: {errors}")
    
    # Create parent dir if needed
    args.out.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Writing triples to {args.out}...")
    g.serialize(destination=args.out, format="turtle")
    logger.info(f"✅ Wrote {len(g)} triples to {args.out}")

if __name__ == "__main__":
    main()
