from __future__ import annotations

import os
from typing import Any, Dict, Iterator, Optional

from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON

from paa_graph_kb.clients.base_client import Client
from paa_graph_kb.models.getty.models import GettyObject, GettyPerson

load_dotenv()


class GettyClient(Client):
    """
    Getty Museum Collection API client.
    
    Since Getty does not provide a public REST search API, this client
    uses the SPARQL endpoint for discovery and paging, then fetches
    full records via their Linked Data URIs.
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        # Default cache_dir
        if cache_dir is None:
            cache_dir = os.getenv("GETTY_OBJ_DIR", "data/getty/objects")

        # Base URL is technically the SPARQL endpoint for discovery
        super().__init__(
            "https://data.getty.edu/museum/collection/sparql",
            apikey=None, # Getty is open
            cache_dir=cache_dir,
            use_cache=use_cache,
        )
        
        self.sparql_endpoint = "https://data.getty.edu/museum/collection/sparql"

    def _iter_sparql_entities(
        self,
        rdf_type: str,
        model_class: Any,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[Any]:
        """Generic iterator for SPARQL-discovered entities."""
        offset = 0
        yielded = 0
        
        while True:
            # 1. Discover Object URIs via SPARQL
            query = f"""
            SELECT DISTINCT ?s WHERE {{
              ?s a <{rdf_type}> .
            }}
            LIMIT {size}
            OFFSET {offset}
            """
            
            sparql = SPARQLWrapper(self.sparql_endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            
            try:
                results = sparql.query().convert()
                bindings = results["results"]["bindings"]
            except Exception as e:
                print(f"SPARQL query failed: {e}")
                break
                
            if not bindings:
                break
                
            # 2. Fetch full JSON-LD for each entity
            for row in bindings:
                url = row["s"]["value"]
                
                if not url.startswith("http"):
                    continue
                    
                try:
                    data = self._request(url)
                    if data:
                        obj = model_class.model_validate(data)
                        yield obj
                        yielded += 1
                        
                        if limit is not None and yielded >= limit:
                            return
                except Exception as e:
                    print(f"Failed to fetch or parse {url}: {e}")
                    continue
            
            offset += size
            if len(bindings) < size:
                break

    def iter_objects(
        self,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[GettyObject]:
        """Iterate over Getty Museum objects."""
        return self._iter_sparql_entities(
            "http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object",
            GettyObject,
            size=size,
            limit=limit
        )

    def iter_people(
        self,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[GettyPerson]:
        """Iterate over Getty People."""
        return self._iter_sparql_entities(
            "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
            GettyPerson,
            size=size,
            limit=limit
        )

def _main():
    import argparse
    ap = argparse.ArgumentParser(description="Quick sanity test for GettyClient.")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--size", type=int, default=10)
    args = ap.parse_args()

    client = GettyClient()
    print(f"Fetching up to {args.limit} objects from Getty...")
    
    count = 0
    for obj in client.iter_objects(size=args.size, limit=args.limit):
        print(f"[{count+1}] {obj.id} - {obj.label}")
        count += 1

    print(f"\nFetching up to {args.limit} people from Getty...")
    count = 0
    for person in client.iter_people(size=args.size, limit=args.limit):
        print(f"[{count+1}] {person.id} - {person.label}")
        count += 1

if __name__ == "__main__":
    _main()

