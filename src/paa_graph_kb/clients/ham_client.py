from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Type, TypeVar
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

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


class Client:
    """Reusable HTTP client with retries, backoff, and paging helpers with optional caching."""

    def __init__(
        self,
        base_url: str,
        apikey: str,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        self.apikey = apikey
        self.base = base_url.rstrip("/")

        self.timeout: float = 30.0
        self.max_retries: int = 5
        self.backoff_initial: float = 0.5
        self.backoff_max: float = 10.0
        self.user_agent = "paa-graph-kb/0.1"
        self.session = requests.Session()

        self.env_prefix: str = ""
        self.session.headers.update({"User-Agent": self.user_agent})

        # Caching setup
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir and self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ---------- URL / HTTP helpers ----------

    @staticmethod
    def _merge_query(url: str, **extra: Any) -> str:
        parts = list(urlparse(url))
        q = dict(parse_qsl(parts[4], keep_blank_values=True))
        q.update({k: v for k, v in extra.items() if v is not None})
        parts[4] = urlencode(q, doseq=True)
        return urlunparse(parts)

    def _cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key from URL and params."""
        # Normalize the URL and params for consistent hashing
        parts = list(urlparse(url))
        q = dict(parse_qsl(parts[4], keep_blank_values=True))
        if params:
            q.update({k: v for k, v in params.items() if v is not None})

        # Remove apikey from cache key (so different users can share cache)
        q.pop("apikey", None)

        # Sort for consistent ordering
        sorted_params = sorted(q.items())
        cache_string = f"{parts[2]}?{urlencode(sorted_params)}"  # path + sorted params

        # Create a short hash
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]

    def _get_cache_path(self, cache_key: str) -> Optional[Path]:
        """Get the file path for a cache key."""
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{cache_key}.json"

    def _read_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Read response from cache if available."""
        if not self.use_cache or not self.cache_dir:
            return None

        cache_path = self._get_cache_path(cache_key)
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If cache is corrupted, ignore it
                return None
        return None

    def _write_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Write response to cache."""
        if not self.use_cache or not self.cache_dir:
            return

        cache_path = self._get_cache_path(cache_key)
        if cache_path:
            try:
                with open(cache_path, 'w') as f:
                    json.dump(data, f, indent=2)
            except IOError:
                # If we can't write cache, just continue
                pass

    def _request(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build the final URL by *merging* existing query and params (de-duping apikey)."""
        parts = list(urlparse(url))
        q = dict(parse_qsl(parts[4], keep_blank_values=True))  # existing query on URL

        # Merge in caller params
        if params:
            # don't mutate caller
            for k, v in params.items():
                if v is not None:
                    q[k] = v

        # Ensure apikey present exactly once
        if "apikey" not in q:
            q["apikey"] = self.apikey

        # Recompose final URL
        parts[4] = urlencode(q, doseq=True)
        final_url = urlunparse(parts)

        # Check cache first
        cache_key = self._cache_key(url, params)
        cached_data = self._read_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Not in cache, fetch from API
        attempt = 0
        delay = self.backoff_initial
        while True:
            try:
                resp = self.session.get(final_url, timeout=self.timeout)
                if resp.status_code in (429, 500, 502, 503, 504):
                    ra = resp.headers.get("Retry-After")
                    if ra:
                        try:
                            time.sleep(min(float(ra), self.backoff_max))
                        except Exception:
                            pass
                    raise requests.HTTPError(
                        f"Retryable status: {resp.status_code}", response=resp
                    )
                resp.raise_for_status()
                data = resp.json()

                # Write to cache
                self._write_cache(cache_key, data)

                return data
            except requests.HTTPError:
                attempt += 1
                if attempt > self.max_retries:
                    raise
                time.sleep(min(delay, self.backoff_max))
                delay *= 2.0
            except requests.RequestException:
                attempt += 1
                if attempt > self.max_retries:
                    raise
                time.sleep(min(delay, self.backoff_max))
                delay *= 2.0

    def _endpoint(self, path: str) -> str:
        return f"{self.base}/{path.lstrip('/')}"

    # ---------- Paging ----------

    def _iter_pages(
        self, path: str, params: Optional[Dict[str, Any]] = None, *, size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        q = dict(params or {})
        q.setdefault("size", size)

        first_url = self._endpoint(path)
        data = self._request(first_url, params=q)
        yield data

        info = (data or {}).get("info") or {}
        next_url = info.get("next")
        page = info.get("page")
        pages = info.get("pages")

        if not next_url and page and pages and page < pages:
            next_url = self._merge_query(first_url, **q, page=page + 1)

        while next_url:
            data = self._request(next_url, params={})
            yield data
            info = (data or {}).get("info") or {}
            next_url = info.get("next")
            page = info.get("page")
            pages = info.get("pages")
            if not next_url and page and pages and page < pages:
                next_url = self._merge_query(first_url, **q, page=page + 1)

    # ---------- Model iteration ----------

    def _iter_model(
        self,
        path: str,
        page_model: Type[PageT],
        record_model: Type[ModelT],
        params: Optional[Dict[str, Any]] = None,
        *,
        size: int = 100,
        limit: Optional[int] = None,
        strict: bool = False,
    ) -> Iterator[ModelT]:
        yielded = 0
        for raw in self._iter_pages(path, params=params, size=size):
            page = page_model.model_validate(raw)
            for rec in page.records:
                if isinstance(rec, dict):
                    try:
                        item = record_model.model_validate(rec)
                    except ValidationError:
                        if strict:
                            raise
                        continue
                else:
                    item = rec
                yield item
                yielded += 1
                if limit is not None and yielded >= limit:
                    return


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
