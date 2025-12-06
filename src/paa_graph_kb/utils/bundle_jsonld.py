"""
Script to bundle multiple JSON-LD files into a single JSON array file.
"""

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Bundle JSON-LD files.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory containing JSON files")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON file")
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        logger.error(f"Input directory not found: {args.input_dir}")
        exit(1)
        
    data = []
    files = list(args.input_dir.glob("*.json"))
    logger.info(f"Found {len(files)} files in {args.input_dir}")
    
    for p in files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                # Load and strip wrapper if necessary (like HAM pages)
                # But for Getty, we expect the root object.
                # For robustness, just load.
                content = json.load(f)
                data.append(content)
        except Exception as e:
            logger.error(f"Error reading {p}: {e}")
            
    # Create parent dir
    args.output.parent.mkdir(parents=True, exist_ok=True)
            
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    logger.info(f"✅ Bundled {len(data)} records into {args.output}")

if __name__ == "__main__":
    main()
