"""
Script to analyze bibliographic records in the Perseus Linked Art graph.
Identifies 'dirty' records containing HTML/TEI markup to support the curation workflow.
"""

import argparse
import csv
import logging
import re
from pathlib import Path

from rdflib import Graph, Namespace

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Namespaces
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
AAT = Namespace("http://vocab.getty.edu/aat/")

# Regex for detecting HTML/XML tags
TAG_REGEX = re.compile(r"<[^>]+>")

def analyze_bibliographies(graph_path: Path, report_path: Path):
    logger.info(f"Loading graph from {graph_path}...")
    g = Graph()
    g.parse(graph_path, format="turtle")
    logger.info(f"Loaded {len(g)} triples.")

    # Query for bibliographic notes
    # aat:300026497 = "bibliography (documents)"
    query = """
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX aat: <http://vocab.getty.edu/aat/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?obj ?note ?content
    WHERE {
        ?obj crm:P67i_is_referred_to_by ?note .
        ?note crm:P2_has_type aat:300026497 ;
              crm:P190_has_symbolic_content ?content .
    }
    """
    
    results = g.query(query)
    logger.info(f"Found {len(results)} bibliographic entries.")

    total = 0
    dirty_count = 0
    tags_found = {}

    # Prepare CSV report
    with open(report_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Object URI", "Note URI", "Has Markup", "Content Preview"])

        for row in results:
            total += 1
            content = str(row.content)
            has_markup = False
            
            # Check for tags
            matches = TAG_REGEX.findall(content)
            if matches:
                has_markup = True
                dirty_count += 1
                for tag in matches:
                    # Simplify tag to name (e.g., <p> -> p, </hi> -> hi)
                    tag_name = re.sub(r"[</>]", "", tag.split()[0])
                    tags_found[tag_name] = tags_found.get(tag_name, 0) + 1

            writer.writerow([
                str(row.obj), 
                str(row.note), 
                "Yes" if has_markup else "No", 
                content[:200].replace("\n", " ") + "..." if len(content) > 200 else content
            ])

    logger.info(f"\nAnalysis Complete:")
    logger.info(f"  Total Bibliographies: {total}")
    logger.info(f"  Entries with Markup:  {dirty_count} ({dirty_count/total*100:.1f}%)")
    logger.info(f"  Clean Entries:        {total - dirty_count}")
    
    if tags_found:
        logger.info("\nMarkup Tags Found:")
        for tag, count in sorted(tags_found.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  <{tag}>: {count}")

    logger.info(f"\nDetailed report saved to {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Analyze Perseus bibliographies.")
    parser.add_argument(
        "--graph", 
        type=Path, 
        default=Path("data/perseus/perseus_linked_art.ttl"),
        help="Path to Perseus Linked Art graph"
    )
    parser.add_argument(
        "--out", 
        type=Path, 
        default=Path("data/reports/bibliography_audit.csv"),
        help="Output path for CSV report"
    )
    
    args = parser.parse_args()
    
    args.out.parent.mkdir(parents=True, exist_ok=True)
    analyze_bibliographies(args.graph, args.out)

if __name__ == "__main__":
    main()
