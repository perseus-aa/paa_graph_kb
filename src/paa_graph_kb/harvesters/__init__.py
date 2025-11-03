from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable

from rdflib import Graph


class Harvester(ABC):
    """
    Abstract base class for all museum data harvesters.

    A Harvester is responsible for:
      1. Fetching records from a remote API (using a Client subclass)
      2. Transforming them into a common staging RDF form
      3. Writing them to disk as Turtle or RDF

    Each concrete subclass should implement `fetch()` and `stage()`.
    """

    @abstractmethod
    def fetch(self, limit: int = 100, **kwargs) -> Iterable[Any]:
        """Fetch raw or Pydantic-validated records from the source API."""
        ...

    @abstractmethod
    def stage(self, records: Iterable[Any], out_path: Path) -> Graph:
        """Convert records into staging triples and write them to a Turtle file."""
        ...

    def run(self, out_path: Path, limit: int = 100, **kwargs) -> Path:
        """
        Convenience method: fetch + stage in one step.
        Returns the path to the written TTL file.
        """
        records = list(self.fetch(limit=limit, **kwargs))
        graph = self.stage(records, out_path)
        graph.serialize(destination=out_path, format="turtle")
        print(f"✅ {len(graph)} triples written to {out_path}")
        return out_path
