from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Type, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from paa_graph_kb.clients.base_client import Client
from paa_graph_kb.models.ham.models import (
    HAMObject,
    HAMPage,
    HAMPeriod,
    HAMPerson,
    HAMPlace,
    HAMPublication,
    PeriodPage,
    PersonPage,
    PlacePage,
    PublicationPage,
)

ModelT = TypeVar("ModelT", bound=BaseModel)
PageT = TypeVar("PageT", bound=BaseModel)

load_dotenv()


class HAMClient(Client):
    """Harvard Art Museums API client with optional caching."""

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        # Default cache_dir from environment if not specified
        if cache_dir is None:
            cache_dir = os.getenv("OBJ_DIR", "data/ham/objects")

        super().__init__(
            os.getenv("HAM_API_BASE"),
            os.getenv("HAM_APIKEY"),
            cache_dir=cache_dir,
            use_cache=use_cache,
        )

    def iter_objects(
        self,
        params: Optional[Dict[str, Any]] = None,
        *,
        size: int = 100,
        limit: Optional[int] = None,
        strict: bool = False,
    ) -> Iterator[HAMObject]:
        return self._iter_model(
            "object", HAMPage, HAMObject, params, size=size, limit=limit, strict=strict
        )

    def iter_periods(
        self,
        params: Optional[Dict[str, Any]] = None,
        *,
        size: int = 100,
        limit: Optional[int] = None,
        strict: bool = False,
    ) -> Iterator[HAMPeriod]:
        return self._iter_model(
            "period",
            PeriodPage,
            HAMPeriod,
            params,
            size=size,
            limit=limit,
            strict=strict,
        )

    def iter_places(
        self,
        params: Optional[Dict[str, Any]] = None,
        *,
        size: int = 100,
        limit: Optional[int] = None,
        strict: bool = False,
    ) -> Iterator[HAMPlace]:
        return self._iter_model(
            "place", PlacePage, HAMPlace, params, size=size, limit=limit, strict=strict
        )

    def iter_people(
        self,
        params: Optional[Dict[str, Any]] = None,
        *,
        size: int = 100,
        limit: Optional[int] = None,
        strict: bool = False,
    ) -> Iterator[HAMPerson]:
        return self._iter_model(
            "person",
            PersonPage,
            HAMPerson,
            params,
            size=size,
            limit=limit,
            strict=strict,
        )

    def iter_publications(
        self,
        params: Optional[Dict[str, Any]] = None,
        *,
        size: int = 100,
        limit: Optional[int] = None,
        strict: bool = False,
    ) -> Iterator[HAMPublication]:
        return self._iter_model(
            "publication",
            PublicationPage,
            HAMPublication,
            params,
            size=size,
            limit=limit,
            strict=strict,
        )


# -------- optional self-check harness --------


def _parse_params(pairs):
    out: Dict[str, Any] = {}
    for p in pairs or []:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k] = v
        else:
            out[p] = "1"
    return out


def _main():
    ap = argparse.ArgumentParser(description="Quick sanity test for HAMClient.")
    ap.add_argument(
        "--test",
        choices=["objects", "periods", "places", "people", "publications"],
        default="objects",
    )
    ap.add_argument(
        "--env-prefix",
        default="HAM_",
        help="Environment variable prefix for BASE/APIKEY (default: HAM_)",
    )
    ap.add_argument("--apikey", help="Override API key explicitly")
    ap.add_argument("--base", help="Override base URL explicitly")
    ap.add_argument(
        "--params",
        nargs="*",
        help="Query params as key=value (e.g., culture=Greek hasimage=1)",
    )
    ap.add_argument("--size", type=int, default=100)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    client = HAMClient(
        base_url=args.base, apikey=args.apikey, env_prefix=args.env_prefix
    )
    params = _parse_params(args.params)

    iters = {
        "objects": client.iter_objects,
        "periods": client.iter_periods,
        "places": client.iter_places,
        "people": client.iter_people,
        "publications": client.iter_publications,
    }

    it = iters[args.test](
        params=params, size=args.size, limit=args.limit, strict=args.strict
    )
    rows = list(it)
    print(
        f"Fetched {len(rows)} {args.test}. Sample:\n{rows[0] if rows else '<<empty>>'}"
    )


if __name__ == "__main__":
    _main()
