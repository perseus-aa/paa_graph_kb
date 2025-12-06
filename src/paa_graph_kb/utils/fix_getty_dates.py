"""
Script to fix invalid ISO 8601 dates in cached Getty JSON-LD files.
Specifically targets 3-digit negative years (e.g., "-500-12-31") which cause RDFLib parsing errors.
Converts them to 4-digit format (e.g., "-0500-12-31").
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Union

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Regex to identify 3-digit negative years at start of string
# Matches "-123-" followed by anything
DATE_REGEX = re.compile(r'^-(\d{3})-(.*)')

def fix_date_string(value: str) -> str:
    """
    Pad 3-digit negative years with a leading zero.
    Example: "-500-12-31T23:59:59" -> "-0500-12-31T23:59:59"
    """
    match = DATE_REGEX.match(value)
    if match:
        # Extract parts
        year_digits = match.group(1)
        rest = match.group(2)
        # Reconstruct with padded year
        fixed_value = f"-0{year_digits}-{rest}"
        return fixed_value
    return value

def traverse_and_fix(data: Union[Dict, List, Any]) -> bool:
    """
    Recursively traverse JSON structure and fix date fields in place.
    Returns True if any change was made.
    """
    changed = False
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Target keys
            if key in ["begin_of_the_begin", "end_of_the_end"]:
                if isinstance(value, str):
                    fixed = fix_date_string(value)
                    if fixed != value:
                        data[key] = fixed
                        changed = True
            
            # Recurse
            elif isinstance(value, (dict, list)):
                if traverse_and_fix(value):
                    changed = True
                    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                if traverse_and_fix(item):
                    changed = True
                    
    return changed

def process_files(directory: Path):
    """Iterate over JSON files and apply fixes."""
    files = list(directory.glob("*.json"))
    logger.info(f"Found {len(files)} JSON files in {directory}")
    
    fixed_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if traverse_and_fix(data):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                fixed_count += 1
                logger.debug(f"Fixed dates in {file_path.name}")
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            
    logger.info(f"Process complete. Fixed {fixed_count} files.")

def main():
    parser = argparse.ArgumentParser(description="Fix invalid dates in Getty JSON-LD.")
    parser.add_argument(
        "--dir", 
        type=Path, 
        default=Path("data/getty/objects"),
        help="Directory containing cached Getty JSON-LD files"
    )
    
    args = parser.parse_args()
    
    if not args.dir.exists():
        logger.error(f"Directory not found: {args.dir}")
        return
        
    process_files(args.dir)

if __name__ == "__main__":
    main()
