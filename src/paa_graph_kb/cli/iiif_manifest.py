import typer
from typing import Annotated, Optional, Dict, Any, List
from rich.console import Console
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import json
import os
import re
import hashlib

app = typer.Typer(help="Generate IIIF Manifests from the Knowledge Base.")
console = Console()

# --- Environment Loading ---
def load_graphdb_env():
    env_path = os.path.join(os.path.dirname(__file__), '../graphdb/graphdb_env')
    env_path = os.path.abspath(env_path)
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    match = re.match(r'(\w+)\s*=\s*(.*)', line)
                    if match:
                        os.environ[match.group(1)] = match.group(2).strip("'\"")

load_graphdb_env()
GRAPHDB_BASE = os.getenv("GRAPHDB_BASE")
REPOSITORY = os.getenv("REPOSITORY")

def get_sparql_results(query: str):
    if not GRAPHDB_BASE or not REPOSITORY:
        console.log("[bold red]ERROR:[/bold red] GraphDB environment not configured.")
        raise typer.Exit(code=1)

    sparql = SPARQLWrapper(f"{GRAPHDB_BASE}/repositories/{REPOSITORY}")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception as e:
        console.log(f"[bold red]ERROR:[/bold red] SPARQL query failed: {e}")
        raise typer.Exit(code=1)

def fetch_iiif_info(service_url: str) -> Dict[str, Any]:
    """Fetch dimensions from IIIF info.json if missing."""
    info_url = f"{service_url}/info.json"
    try:
        response = requests.get(info_url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        console.log(f"[yellow]Warning:[/yellow] Failed to fetch info.json from {info_url}: {e}")
    return {}

@app.command(name="generate")
def generate_manifest(
    object_uri: Annotated[str, typer.Argument(help="The URI of the object to generate a manifest for.")],
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output file path (default: stdout)")] = None,
    fetch_dims: Annotated[bool, typer.Option("--fetch-dims", help="Fetch missing dimensions from IIIF service")] = True
):
    """
    Generate a IIIF Presentation 3.0 Manifest for a given object URI.
    """
    
    # 1. Get Object Metadata
    metadata_query = f"""
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?label ?desc WHERE {{
      <{object_uri}> rdfs:label ?label .
      OPTIONAL {{ <{object_uri}> crm:P3_has_note ?desc }}
    }} LIMIT 1
    """
    meta_results = get_sparql_results(metadata_query)
    
    if not meta_results:
        console.log(f"[bold red]Error:[/bold red] Object not found: {object_uri}")
        raise typer.Exit(code=1)
        
    obj_label = meta_results[0]["label"]["value"]
    obj_desc = meta_results[0].get("desc", {}).get("value", "")

    # 2. Get Images
    # Covers both HAM (via DigitalObject) and Perseus (via VisualItem) paths
    # Prioritizes la:access_point (real URL) over service node URI (which might be a local proxy)
    images_query = f"""
    PREFIX la: <https://linked.art/ns/terms/>
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT DISTINCT ?imageLabel ?iiifService ?accessPoint ?width ?height WHERE {{
      BIND(<{object_uri}> AS ?obj)
      
      {{
        # HAM Style
        ?obj la:digitally_shown_by ?digitalObj .
        ?digitalObj a la:DigitalObject ;
                    la:digitally_available_via ?iiifService .
        OPTIONAL {{ ?iiifService la:access_point ?accessPoint }}
        OPTIONAL {{ ?digitalObj crm:P43_has_dimension [ crm:P2_has_type <http://vocab.getty.edu/aat/300055647> ; crm:P90_has_value ?width ] }}
        OPTIONAL {{ ?digitalObj crm:P43_has_dimension [ crm:P2_has_type <http://vocab.getty.edu/aat/300055644> ; crm:P90_has_value ?height ] }}
        OPTIONAL {{ ?digitalObj rdfs:label ?imageLabel }}
      }}
      UNION
      {{
        # Perseus Style (Object -> VisualItem -> Service)
        ?obj la:digitally_shown_by ?visualItem .
        ?visualItem la:digitally_shown_by ?iiifService .
        OPTIONAL {{ ?iiifService la:access_point ?accessPoint }}
        OPTIONAL {{ ?visualItem rdfs:label ?imageLabel }}
        # Dimensions typically missing for Perseus in graph
      }}
    }}
    """
    image_results = get_sparql_results(images_query)
    
    if not image_results:
        console.log("[yellow]Warning:[/yellow] No images found for this object.")
    
    # 3. Construct Manifest
    manifest_id = f"https://aa.perseus.org/manifest/{hashlib.sha256(object_uri.encode()).hexdigest()}"
    
    manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": manifest_id,
        "type": "Manifest",
        "label": { "en": [obj_label] },
        "items": []
    }
    
    if obj_desc:
        manifest["summary"] = { "en": [obj_desc] }

    for i, res in enumerate(image_results):
        # Use access_point if available, otherwise fallback to the service node URI
        # This handles cases where the service node is a local proxy (HAM) vs direct URL (Perseus)
        service_url = res.get("accessPoint", {}).get("value")
        if not service_url:
            service_url = res["iiifService"]["value"]

        label = res.get("imageLabel", {}).get("value", f"Image {i+1}")
        
        width = int(res["width"]["value"]) if "width" in res else None
        height = int(res["height"]["value"]) if "height" in res else None
        
        if (width is None or height is None) and fetch_dims:
            console.log(f"Fetching dimensions for {label}...")
            info = fetch_iiif_info(service_url)
            if info:
                width = info.get("width")
                height = info.get("height")
        
        # Fallback defaults if still missing (required for valid canvas)
        if width is None: width = 1000
        if height is None: height = 1000
        
        canvas_id = f"{manifest_id}/canvas/{i+1}"
        
        # Construct Image Body URL (full size)
        # IIIF v2/v3 convention
        image_url = f"{service_url}/full/max/0/default.jpg"

        canvas = {
            "id": canvas_id,
            "type": "Canvas",
            "label": { "en": [label] },
            "height": height,
            "width": width,
            "items": [
                {
                    "id": f"{canvas_id}/page/1",
                    "type": "AnnotationPage",
                    "items": [
                        {
                            "id": f"{canvas_id}/annotation/1",
                            "type": "Annotation",
                            "motivation": "painting",
                            "body": {
                                "id": image_url,
                                "type": "Image",
                                "format": "image/jpeg",
                                "service": [
                                    {
                                        "id": service_url,
                                        "type": "ImageService3",
                                        "profile": "level1"
                                    }
                                ],
                                "height": height,
                                "width": width
                            },
                            "target": canvas_id
                        }
                    ]
                }
            ]
        }
        manifest["items"].append(canvas)

    # Output
    manifest_json = json.dumps(manifest, indent=2)
    
    if output:
        with open(output, 'w') as f:
            f.write(manifest_json)
        console.log(f"[green]Success:[/green] Manifest written to {output}")
    else:
        print(manifest_json)

if __name__ == "__main__":
    app()
