from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, Iterator, List, Optional, Type, TypeVar

import requests
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    confloat,
    field_validator,
)

from paa.models.ham_models import (
    HAMObject,
    HAMPeriod,
    HAMPerson,
    HAMPlace,
    HAMPublication,
)

# ======================================================
# Unified client for objects + vocab
# ======================================================

T = TypeVar("T", bound=BaseModel)


class HAMClient:
    """Unified client for Harvard Art Museums API.
    Provides iterators over objects, periods, places, people, and publications.
    """

    def __init__(self, apikey: str, base: str = "https://api.harvardartmuseums.org"):
        self.apikey = apikey
        self.base = base.rstrip("/")

    # ---------- Generic iterator over any paginated endpoint ----------
    def _iter_model(
        self,
        endpoint: str,
        model: Type[T],
        params: Optional[Dict[str, Any]] = None,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[T]:
        base_url = f"{self.base}/{endpoint}"
        q = {"apikey": self.apikey, "size": size}
        if params:
            q.update(params)

        count = 0
        with requests.Session() as s:
            url = base_url
            while url:
                resp = s.get(url, params=q if url == base_url else None, timeout=30)
                resp.raise_for_status()
                data = resp.json() or {}

                # If records missing, try single-object shape
                records = data.get("records")
                if records is None:
                    yield model.model_validate(data)
                    return

                for raw in records:
                    yield model.model_validate(raw)
                    count += 1
                    if limit is not None and count >= limit:
                        return

                info = data.get("info") or {}
                next_url = info.get("next")
                url = str(next_url) if next_url else None

    # ---------- Objects ----------
    def iter_objects(
        self,
        params: Optional[Dict[str, Any]] = None,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[HAMObject]:
        return self._iter_model(
            "object", HAMObject, params=params, size=size, limit=limit
        )

    # ---------- Periods ----------
    def iter_periods(
        self,
        params: Optional[Dict[str, Any]] = None,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[HAMPeriod]:
        return self._iter_model(
            "period", HAMPeriod, params=params, size=size, limit=limit
        )

    def get_period(self, period_id: int) -> HAMPeriod:
        url = f"{self.base}/period/{period_id}?apikey={self.apikey}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return HAMPeriod.model_validate(resp.json() or {})

    # ---------- Places ----------
    def iter_places(
        self,
        params: Optional[Dict[str, Any]] = None,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[HAMPlace]:
        return self._iter_model(
            "place", HAMPlace, params=params, size=size, limit=limit
        )

    def get_place(self, place_id: int) -> HAMPlace:
        url = f"{self.base}/place/{place_id}?apikey={self.apikey}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return HAMPlace.model_validate(resp.json() or {})

    # ---------- People ----------
    def iter_people(
        self,
        params: Optional[Dict[str, Any]] = None,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[HAMPerson]:
        return self._iter_model(
            "person", HAMPerson, params=params, size=size, limit=limit
        )

    def get_person(self, person_id: int) -> HAMPerson:
        url = f"{self.base}/person/{person_id}?apikey={self.apikey}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return HAMPerson.model_validate(resp.json() or {})

    # ---------- Publications ----------
    def iter_publications(
        self,
        params: Optional[Dict[str, Any]] = None,
        size: int = 100,
        limit: Optional[int] = None,
    ) -> Iterator[HAMPublication]:
        return self._iter_model(
            "publication", HAMPublication, params=params, size=size, limit=limit
        )

    def get_publication(self, publication_id: int) -> HAMPublication:
        url = f"{self.base}/publication/{publication_id}?apikey={self.apikey}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return HAMPublication.model_validate(resp.json() or {})
