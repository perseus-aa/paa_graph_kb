"""
Prototype script to demonstrate the "Bibliography Explosion" workflow.
Simulates parsing a legacy HTML bibliography blob into distinct W3C Web Annotations.
"""

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import List, Dict

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Namespaces
OA = Namespace("http://www.w3.org/ns/oa#")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PAA = Namespace("https://aa.perseus.org/id/")
STG = Namespace("https://aa.perseus.org/staging#")

# Sample "Dirty" Input from Perseus (similar to what we analyzed)
SAMPLE_BLOB = """
<P><bibl>Beazley, ABV</bibl>, p. 23, no. 1; <bibl>Boardman 1974</bibl>, fig. 45; 
<bibl>CVA, USA fasc. 17, Toledo fasc. 1</bibl>, pp. 20-21, pls. 30, 31.</P>
"""

TARGET_OBJECT_URI = "https://aa.perseus.org/id/thing/12345-sample-object"

def parse_bibliography_blob(text: str) -> List[Dict[str, str]]:
    """
    Heuristic splitter to simulate an Agent parsing the blob.
    In production, this would be an LLM or sophisticated parser.
    """
    # 1. Remove outer P tags
    clean = re.sub(r'</?P>', '', text, flags=re.IGNORECASE).strip()
    
    # 2. Split by semicolon (common delimiter in Perseus data)
    raw_chunks = clean.split(';')
    
    citations = []
    
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
            
        # Extraction heuristic:
        # Look for content inside <bibl>...</bibl> as the "Work" title/abbr
        # Look for text after </bibl> as the "Scope" (pages, plates)
        
        bibl_match = re.search(r'<bibl>(.*?)</bibl>(.*)', chunk, re.IGNORECASE | re.DOTALL)
        
        if bibl_match:
            work_title = bibl_match.group(1).strip()
            scope = bibl_match.group(2).strip().strip(',')
            
            citations.append({
                "type": "citation",
                "source_work": work_title,
                "scope": scope,
                "original_text": chunk
            })
        else:
            # Fallback: It's just text
            citations.append({
                "type": "text",
                "content": chunk
            })
            
    return citations

def generate_annotation_graph(target_uri: str, parsed_items: List[Dict[str, str]]) -> Graph:
    """
    Constructs W3C Web Annotations from parsed items.
    """
    g = Graph()
    g.bind("oa", OA)
    g.bind("crm", CRM)
    g.bind("dcterms", DCTERMS)
    g.bind("paa", PAA)
    
    target = URIRef(target_uri)
    
    for item in parsed_items:
        # Mint a UUID for this new annotation
        anno_uuid = str(uuid.uuid4())
        anno_uri = PAA[f"annotation/{anno_uuid}"]
        
        # 1. The Annotation Node
        g.add((anno_uri, RDF.type, OA.Annotation))
        g.add((anno_uri, OA.hasTarget, target))
        g.add((anno_uri, DCTERMS.created, Literal(datetime.now(timezone.utc).isoformat(), datatype=XSD.dateTime)))
        g.add((anno_uri, DCTERMS.creator, Literal("paa-splitter-agent-v1")))
        
        # 2. The Body (Content)
        if item["type"] == "citation":
            g.add((anno_uri, OA.motivatedBy, OA.referencing))
            
            # Create a Bibliographic Reference Node (E33)
            # This represents the specific citation instance (e.g., "Beazley, p. 23")
            ref_node = PAA[f"reference/{uuid.uuid4()}"]
            g.add((anno_uri, OA.hasBody, ref_node))
            g.add((ref_node, RDF.type, CRM.E33_Linguistic_Object))
            g.add((ref_node, RDFS.label, Literal(f"Citation: {item['source_work']}")))
            
            # Link to the abstract Work (Concept/Authority) - simulated
            # In a real system, we would look up "ABV" to find <https://aa.perseus.org/id/work/abv>
            # Here we just create a placeholder/blank node or literal for the work
            g.add((ref_node, CRM.P67_refers_to, Literal(item['source_work']))) # The "Work"
            
            # Store the scope (pages, plates)
            if item['scope']:
                g.add((ref_node, CRM.P190_has_symbolic_content, Literal(item['scope'])))
                
        else:
            # Just a textual note (unparsed)
            g.add((anno_uri, OA.motivatedBy, OA.describing))
            
            body_node = BNode()
            g.add((anno_uri, OA.hasBody, body_node))
            g.add((body_node, RDF.type, OA.TextualBody))
            g.add((body_node, RDF.value, Literal(item['content'])))
            g.add((body_node, DCTERMS.format, Literal("text/plain")))

    return g

def main():
    print("--- INPUT BLOB ---")
    print(SAMPLE_BLOB.strip())
    print("\n--- AI AGENT PARSING ---")
    
    parsed = parse_bibliography_blob(SAMPLE_BLOB)
    for i, p in enumerate(parsed):
        print(f"[{i+1}] Type: {p['type']}")
        if p['type'] == 'citation':
            print(f"    Work:  {p['source_work']}")
            print(f"    Scope: {p['scope']}")
        else:
            print(f"    Text:  {p['content']}")
            
    print("\n--- GENERATED RDF (Web Annotations) ---")
    g = generate_annotation_graph(TARGET_OBJECT_URI, parsed)
    print(g.serialize(format="turtle"))

if __name__ == "__main__":
    main()
