import datetime as dt
import re
from datetime import date, datetime
from typing import Any, Dict, Iterator, List, Optional, Type, TypeVar

from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    confloat,
    field_validator,
)

# ======================================================
# Common page envelope
# ======================================================


class PageInfo(BaseModel):
    page: Optional[int] = None
    pages: Optional[int] = None
    totalrecords: Optional[int] = None
    next: Optional[AnyUrl] = None
    prev: Optional[AnyUrl] = None


# ======================================================
# Object endpoint models
# ======================================================


class Color(BaseModel):
    color: str
    spectrum: Optional[str] = None
    hue: Optional[str] = None
    percent: Optional[confloat(ge=0.0, le=1.0)] = None
    css3: Optional[str] = None


class Image(BaseModel):
    image_date: Optional[dt.date] = Field(default=None, alias="date")
    copyright: Optional[str] = None
    imageid: Optional[int] = None
    idsid: Optional[int] = None
    format: Optional[str] = None
    description: Optional[str] = None
    technique: Optional[str] = None
    renditionnumber: Optional[str] = None
    displayorder: Optional[int] = None
    baseimageurl: Optional[HttpUrl] = None
    alttext: Optional[str] = None
    width: Optional[int] = None
    publiccaption: Optional[str] = None
    iiifbaseuri: Optional[HttpUrl] = None
    height: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_validator("image_date", mode="before")
    @classmethod
    def _parse_date(cls, v):
        if v in (None, "", "null"):
            return None
        if isinstance(v, dt.date) and not isinstance(v, dt.datetime):
            return v
        if isinstance(v, dt.datetime):
            return v.date()
        if isinstance(v, str):
            # Try ISO first
            try:
                return dt.datetime.fromisoformat(v.replace("Z", "+00:00")).date()
            except Exception:
                # Then just YYYY-MM-DD
                try:
                    return dt.date.fromisoformat(v[:10])
                except Exception:
                    return None
        return None


class TermItem(BaseModel):
    name: str
    id: Optional[int] = None


class Terms(BaseModel):
    culture: Optional[List[TermItem]] = None
    medium: Optional[List[TermItem]] = None
    technique: Optional[List[TermItem]] = None
    model_config = ConfigDict(extra="ignore")


class TitleItem(BaseModel):
    titletype: Optional[str] = None
    titleid: Optional[int] = None
    displayorder: Optional[int] = None
    title: str


class WorkType(BaseModel):
    worktypeid: Optional[int] = None
    worktype: str


class SeeAlsoItem(BaseModel):
    id: Optional[AnyUrl] = None
    type: Optional[str] = None
    format: Optional[str] = None
    profile: Optional[AnyUrl] = None


class HAMObject(BaseModel):
    # Identifiers
    id: int
    objectid: int
    objectnumber: Optional[str] = None

    # Dating
    accessionyear: Optional[int] = None
    dated: Optional[str] = None
    datebegin: Optional[int] = None
    dateend: Optional[int] = None
    period: Optional[str] = None
    periodid: Optional[int] = None
    century: Optional[str] = None
    culture: Optional[str] = None

    # Classification / type
    classification: Optional[str] = None
    classificationid: Optional[int] = None
    worktypes: Optional[List[WorkType]] = None
    style: Optional[str] = None
    technique: Optional[str] = None
    techniqueid: Optional[int] = None
    medium: Optional[str] = None

    # Textuals
    description: Optional[str] = None
    commentary: Optional[str] = None
    labeltext: Optional[str] = None
    signed: Optional[str] = None
    state: Optional[str] = None
    edition: Optional[str] = None
    standardreferencenumber: Optional[str] = None
    dimensions: Optional[str] = None
    creditline: Optional[str] = None
    provenance: Optional[str] = None
    accessionmethod: Optional[str] = None

    # Institutional
    department: Optional[str] = None
    division: Optional[str] = None
    contact: Optional[str] = None

    # Counts & analytics
    imagecount: Optional[int] = None
    mediacount: Optional[int] = None
    colorcount: Optional[int] = None
    markscount: Optional[int] = None
    peoplecount: Optional[int] = None
    titlescount: Optional[int] = None
    publicationcount: Optional[int] = None
    exhibitioncount: Optional[int] = None
    contextualtextcount: Optional[int] = None
    groupcount: Optional[int] = None
    relatedcount: Optional[int] = None
    totalpageviews: Optional[int] = None
    totaluniquepageviews: Optional[int] = None
    verificationlevel: Optional[int] = None
    verificationleveldescription: Optional[str] = None
    imagepermissionlevel: Optional[int] = None
    lendingpermissionlevel: Optional[int] = None
    accesslevel: Optional[int] = None
    rank: Optional[int] = None

    # Web & dates
    url: Optional[HttpUrl] = None
    createdate: Optional[datetime] = None
    lastupdate: Optional[datetime] = None
    dateoffirstpageview: Optional[date] = None
    dateoflastpageview: Optional[date] = None

    # Color & media
    colors: Optional[List[Color]] = None
    images: Optional[list[Image]] = None
    primaryimageurl: Optional[HttpUrl] = None

    # Terms & titles
    terms: Optional[Terms] = None
    titles: Optional[List[TitleItem]] = None
    title: Optional[str] = None

    # See also (e.g., IIIF manifest)
    seeAlso: Optional[List[SeeAlsoItem]] = Field(default=None, alias="seeAlso")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_validator(
        "description",
        "commentary",
        "labeltext",
        "provenance",
        "creditline",
        "signed",
        "state",
        "edition",
        "dimensions",
        "title",
        mode="before",
    )
    @classmethod
    def _normalize_crlf(cls, v: Any) -> Any:
        """Normalize CRLF and stray ^M characters; trim excessive interior whitespace."""
        if not isinstance(v, str):
            return v
        v = v.replace("\r\n", "\n").replace("\r", "\n")
        v = v.replace("\x0d", "\n")
        v = re.sub(r"\n{3,}", "\n\n", v)
        return v.strip()


class HAMPage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMObject]


# ======================================================
# Vocabulary endpoint models
# ======================================================


class HAMPeriod(BaseModel):
    id: int
    name: Optional[str] = None
    displayname: Optional[str] = None
    dated: Optional[str] = None
    datebegin: Optional[int] = None
    dateend: Optional[int] = None
    parentid: Optional[int] = None
    description: Optional[str] = None
    provenance: Optional[str] = None
    createdate: Optional[datetime] = None
    lastupdate: Optional[datetime] = None
    model_config = ConfigDict(extra="ignore")

    @field_validator("description", "provenance", "dated", mode="before")
    @classmethod
    def _normalize_text(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        v = v.replace("\r\n", "\n").replace("\r", "\n").replace("\x0d", "\n")
        v = re.sub(r"\n{3,}", "\n\n", v)
        return v.strip()


class PeriodPage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPeriod]


class Geometry(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wkt: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class HAMPlace(BaseModel):
    id: int
    name: Optional[str] = None
    displayname: Optional[str] = None
    type: Optional[str] = None
    parentid: Optional[int] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    geo: Optional[Geometry] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    createdate: Optional[datetime] = None
    lastupdate: Optional[datetime] = None
    model_config = ConfigDict(extra="ignore")


class PlacePage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPlace]


class HAMPerson(BaseModel):
    id: int
    name: Optional[str] = None
    displayname: Optional[str] = None
    role: Optional[str] = None
    culture: Optional[str] = None
    gender: Optional[str] = None
    birthyear: Optional[int] = None
    deathyear: Optional[int] = None
    born: Optional[str] = None
    died: Optional[str] = None
    birthplace: Optional[str] = None
    deathplace: Optional[str] = None
    url: Optional[HttpUrl] = None
    createdate: Optional[datetime] = None
    lastupdate: Optional[datetime] = None
    model_config = ConfigDict(extra="ignore")

    @field_validator("born", "died", mode="before")
    @classmethod
    def _norm_dates(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        return v.replace("\r\n", "\n").replace("\r", "\n").strip()


class PersonPage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPerson]


class HAMPublication(BaseModel):
    id: int
    title: Optional[str] = None
    subtitle: Optional[str] = None
    citation: Optional[str] = None
    authors: Optional[List[str]] = None
    publishyear: Optional[int] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[AnyUrl] = None
    createdate: Optional[datetime] = None
    lastupdate: Optional[datetime] = None
    model_config = ConfigDict(extra="ignore")

    @field_validator("title", "subtitle", "citation", "publisher", mode="before")
    @classmethod
    def _normalize_text(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        v = v.replace("\r\n", "\n").replace("\r", "\n").replace("\x0d", "\n")
        v = re.sub(r"\n{3,}", "\n\n", v)
        return v.strip()


class PublicationPage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPublication]
