import typer
from typing import Annotated
from rich.console import Console
from rich.table import Table
from rich.text import Text
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import re # Import regex module

app = typer.Typer(help="Browse the Perseus-AA Graph Knowledge Base.")
console = Console()

# --- Custom environment loader for graphdb_env ---
def load_graphdb_env():
    env_path = os.path.join(os.path.dirname(__file__), '../graphdb/graphdb_env')
    env_path = os.path.abspath(env_path)
    console.log(f"DEBUG: Attempting to load env from: {env_path}")
    
    if not os.path.exists(env_path):
        console.log(f"[bold yellow]WARNING:[/bold yellow] GraphDB environment file not found at {env_path}")
        return

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                match = re.match(r'(\w+)\s*=\s*(.*)', line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip("'\"") # Remove quotes
                    os.environ[key] = value
                    # console.log(f"Loaded: {key}={value}") # For debugging

# Load environment variables using the custom loader
load_graphdb_env()
GRAPHDB_BASE = os.getenv("GRAPHDB_BASE")
REPOSITORY = os.getenv("REPOSITORY")

def get_sparql_results(query: str):
    """Executes a SPARQL query against the configured GraphDB endpoint."""
    if not GRAPHDB_BASE or not REPOSITORY:
        console.log("[bold red]ERROR:[/bold red] GraphDB environment variables (GRAPHDB_BASE, REPOSITORY) not set.")
        console.log("Please ensure src/paa_graph_kb/graphdb/graphdb_env is configured or set them in your environment.")
        raise typer.Exit(code=1)

    sparql = SPARQLWrapper(f"{GRAPHDB_BASE}/repositories/{REPOSITORY}")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception as e:
        console.log(f"[bold red]ERROR:[/bold red] Failed to execute SPARQL query: {e}")
        console.log(f"  Attempted endpoint: {GRAPHDB_BASE}/repositories/{REPOSITORY}")
        console.log(f"  Query: {query}")
        raise typer.Exit(code=1)


@app.command(name="search", help="Search for terms in the knowledge base.")
def search_terms(
    term: Annotated[str, typer.Argument(help="The term to search for.")]
):
    """
    Search for terms across different vocabularies and entities in the knowledge base.
    """
    console.print(f"Searching for '[bold magenta]{term}[/bold magenta]'...")

    query = f"""
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT ?entity ?label (SAMPLE(?entityType) AS ?entityTypeSample) (GROUP_CONCAT(?externalUri; SEPARATOR="\\n") AS ?externalUris)
    WHERE {{
      ?entity rdfs:label ?label .
      FILTER (CONTAINS(LCASE(?label), LCASE("{term}")))

      OPTIONAL {{
        ?entity a crm:E55_Type .
        BIND("Concept/Type" AS ?entityType)
      }}
      OPTIONAL {{
        ?entity a crm:E21_Person .
        BIND("Person" AS ?entityType)
      }}
      OPTIONAL {{ ?entity owl:sameAs ?externalUri . }}
    }}
    GROUP BY ?entity ?label
    ORDER BY ?label
    LIMIT 100
    """
    
    results = get_sparql_results(query)

    table = Table(title=f"Search Results for '[bold magenta]{term}[/bold magenta]'")
    table.add_column("Label", style="cyan", no_wrap=False)
    table.add_column("Internal URI", style="green", no_wrap=False)
    table.add_column("External URI(s)", style="blue", no_wrap=False)
    
    if not results:
        console.print(f"No results found for '[bold magenta]{term}[/bold magenta]'.")
        return

    for res in results:
        label = res["label"]["value"]
        entity_uri = res["entity"]["value"]
        external_uris = res.get("externalUris", {}).get("value", "")

        table.add_row(
            label,
            Text(entity_uri, style="link " + entity_uri),
            Text(external_uris.replace("\\n", "\n"), style="link " + external_uris) if external_uris else ""
        )
    
    console.print(table)


@app.command(name="list", help="List terms from specific vocabularies.")
def list_vocab(
    vocabulary: Annotated[str, typer.Argument(help="The vocabulary to list (e.g., 'techniques', 'classifications').")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="Limit the number of results.")] = 50
):
    """
    List terms from a specified vocabulary, with optional filtering and limits.
    """
    console.print(f"Listing '[bold magenta]{vocabulary}[/bold magenta]' (limit: {limit})...")

    where_clause = ""
    if vocabulary.lower() == "techniques":
        where_clause = "{ ?prod crm:P32_used_general_technique ?termUri . }"
    elif vocabulary.lower() == "classifications":
        where_clause = "{ ?obj crm:P2_has_type ?termUri . }"
    else:
        console.print(f"[bold red]ERROR:[/bold red] Unknown vocabulary: '[bold magenta]{vocabulary}[/bold magenta]'. Please choose 'techniques' or 'classifications'.")
        raise typer.Exit(code=1)

    query = f"""
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT ?termUri ?label (GROUP_CONCAT(?externalUri; SEPARATOR="\\n") AS ?externalUris)
    WHERE {{
      ?termUri a crm:E55_Type ;
               rdfs:label ?label .
      
      {where_clause}
      
      OPTIONAL {{ ?termUri owl:sameAs ?externalUri . }}
    }}
    GROUP BY ?termUri ?label
    ORDER BY ?label
    LIMIT {limit}
    """
    
    results = get_sparql_results(query)

    table = Table(title=f"'{vocabulary.capitalize()}' Terms")
    table.add_column("Label", style="cyan", no_wrap=True)
    table.add_column("Internal URI", style="green", no_wrap=False)
    table.add_column("External URI(s)", style="blue", no_wrap=False)

    if not results:
        console.print(f"No terms found for '[bold magenta]{vocabulary}[/bold magenta]'.")
        return

    for res in results:
        label = res["label"]["value"]
        term_uri = res["termUri"]["value"]
        external_uris = res.get("externalUris", {}).get("value", "")

        table.add_row(
            label,
            Text(term_uri, style="link " + term_uri),
            Text(external_uris.replace("\\n", "\n"), style="link " + external_uris) if external_uris else ""
        )
    
    console.print(table)


if __name__ == "__main__":
    app()
