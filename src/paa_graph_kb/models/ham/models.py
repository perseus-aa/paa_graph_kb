from __future__ import annotations
from typing import List, Optional, Dict, Any
import re
import datetime as dt

from pydantic import BaseModel, Field, HttpUrl, AnyUrl, ConfigDict, field_validator, confloat

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

    model_config = ConfigDict(extra='ignore')

    @field_validator('percent', mode='before')
    @classmethod
    def _percent_cast(cls, v: Any) -> Any:
        if v is None:
            return v
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            v = v.strip().rstrip('%')
            try:
                f = float(v)
                # If someone sent 70 (percent) rather than 0.7, normalize heuristically
                return f/100.0 if f > 1.0 else f
            except Exception:
                return None
        return None


class Image(BaseModel):
    # Use a different Python attribute, but accept incoming 'date' via alias
    image_date: Optional[dt.date] = Field(default=None, alias='date')
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

    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    @field_validator('image_date', mode='before')
    @classmethod
    def _parse_image_date(cls, v: Any) -> Optional[dt.date]:
        if v in (None, '', 'null'):
            return None
        if isinstance(v, dt.date) and not isinstance(v, dt.datetime):
            return v
        if isinstance(v, dt.datetime):
            return v.date()
        if isinstance(v, str):
            try:
                return dt.datetime.fromisoformat(v.replace('Z', '+00:00')).date()
            except Exception:
                try:
                    return dt.date.fromisoformat(v[:10])
                except Exception:
                    return None
        return None

    @field_validator('baseimageurl', 'iiifbaseuri', mode='before')
    @classmethod
    def _empty_url_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class TermItem(BaseModel):
    name: str
    id: Optional[int] = None

    model_config = ConfigDict(extra='ignore')


class Terms(BaseModel):
    culture: Optional[List[TermItem]] = None
    medium: Optional[List[TermItem]] = None
    technique: Optional[List[TermItem]] = None
    model_config = ConfigDict(extra='ignore')


class TitleItem(BaseModel):
    titletype: Optional[str] = None
    titleid: Optional[int] = None
    displayorder: Optional[int] = None
    title: str

    model_config = ConfigDict(extra='ignore')


class WorkType(BaseModel):
    worktypeid: Optional[int] = None
    worktype: str

    model_config = ConfigDict(extra='ignore')


class SeeAlsoItem(BaseModel):
    id: Optional[AnyUrl] = None
    type: Optional[str] = None
    format: Optional[str] = None
    profile: Optional[AnyUrl] = None

    model_config = ConfigDict(extra='ignore')

    @field_validator('id', 'profile', mode='before')
    @classmethod
    def _empty_url_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v


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
    createdate: Optional[dt.datetime] = None
    lastupdate: Optional[dt.datetime] = None
    dateoffirstpageview: Optional[dt.date] = None
    dateoflastpageview: Optional[dt.date] = None

    # Color & media
    colors: Optional[List[Color]] = None
    images: Optional[List[Image]] = None
    primaryimageurl: Optional[HttpUrl] = None

    # Terms & titles
    terms: Optional[Terms] = None
    titles: Optional[List[TitleItem]] = None
    title: Optional[str] = None

    # People (artists, makers, etc.)
    people: Optional[List[PersonRef]] = None

    # See also (e.g., IIIF manifest)
    seeAlso: Optional[List[SeeAlsoItem]] = Field(default=None, alias='seeAlso')

    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    # -------- Normalizers / parsers --------

    @field_validator(
        'description', 'commentary', 'labeltext', 'provenance', 'creditline',
        'signed', 'state', 'edition', 'dimensions', 'title', mode='before'
    )
    @classmethod
    def _normalize_crlf(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        v = v.replace('\r\n', '\n').replace('\r', '\n')
        v = v.replace('\x0d', '\n')
        v = re.sub(r'\n{3,}', '\n\n', v)
        return v.strip()

    @field_validator('url', 'primaryimageurl', mode='before')
    @classmethod
    def _empty_url_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator('createdate', 'lastupdate', mode='before')
    @classmethod
    def _parse_datetime(cls, v: Any) -> Optional[dt.datetime]:
        if v in (None, '', 'null'):
            return None
        if isinstance(v, dt.datetime):
            return v
        if isinstance(v, str):
            try:
                return dt.datetime.fromisoformat(v.replace('Z', '+00:00'))
            except Exception:
                return None
        return None

    @field_validator('dateoffirstpageview', 'dateoflastpageview', mode='before')
    @classmethod
    def _parse_date(cls, v: Any) -> Optional[dt.date]:
        if v in (None, '', 'null'):
            return None
        if isinstance(v, dt.date) and not isinstance(v, dt.datetime):
            return v
        if isinstance(v, dt.datetime):
            return v.date()
        if isinstance(v, str):
            try:
                return dt.date.fromisoformat(v[:10])
            except Exception:
                return None
        return None


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
    createdate: Optional[dt.datetime] = None
    lastupdate: Optional[dt.datetime] = None
    model_config = ConfigDict(extra='ignore')

    @field_validator('description', 'provenance', 'dated', mode='before')
    @classmethod
    def _normalize_text(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        v = v.replace('\r\n', '\n').replace('\r', '\n').replace('\x0d', '\n')
        v = re.sub(r'\n{3,}', '\n\n', v)
        return v.strip()


class PeriodPage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPeriod]


class Geometry(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    wkt: Optional[str] = None
    model_config = ConfigDict(extra='ignore')

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def _cast_float(cls, v: Any) -> Optional[float]:
        if v in (None, ''):
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except Exception:
                return None
        return None


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
    createdate: Optional[dt.datetime] = None
    lastupdate: Optional[dt.datetime] = None
    model_config = ConfigDict(extra='ignore')

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def _cast_float_place(cls, v: Any) -> Optional[float]:
        if v in (None, ''):
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except Exception:
                return None
        return None


class PlacePage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPlace]


class PersonRef(BaseModel):
    """Person reference embedded in object records"""
    personid: int
    name: Optional[str] = None
    displayname: Optional[str] = None
    role: Optional[str] = None
    displayorder: Optional[int] = None
    culture: Optional[str] = None
    displaydate: Optional[str] = None
    birthplace: Optional[str] = None
    deathplace: Optional[str] = None
    model_config = ConfigDict(extra='ignore')


class HAMPerson(BaseModel):
    """Full person record from /person endpoint"""
    id: int
    personid: Optional[int] = None
    name: Optional[str] = None
    displayname: Optional[str] = None
    alphasort: Optional[str] = None
    role: Optional[str] = None
    culture: Optional[str] = None
    gender: Optional[str] = None
    displaydate: Optional[str] = None

    # Date information
    birthyear: Optional[int] = None
    deathyear: Optional[int] = None
    datebegin: Optional[int] = None
    dateend: Optional[int] = None
    born: Optional[str] = None
    died: Optional[str] = None
    birthplace: Optional[str] = None
    deathplace: Optional[str] = None

    # Authority identifiers
    lcnaf_id: Optional[str] = None
    ulan_id: Optional[str] = None
    viaf_id: Optional[str] = None
    wikidata_id: Optional[str] = None
    wikipedia_id: Optional[str] = None

    # Metadata
    objectcount: Optional[int] = None
    url: Optional[HttpUrl] = None
    createdate: Optional[dt.datetime] = None
    lastupdate: Optional[dt.datetime] = None
    model_config = ConfigDict(extra='ignore')

    @field_validator('born', 'died', mode='before')
    @classmethod
    def _norm_dates(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        return v.replace('\r\n', '\n').replace('\r', '\n').strip()

    @field_validator('url', mode='before')
    @classmethod
    def _empty_url_to_none_person(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v


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
    createdate: Optional[dt.datetime] = None
    lastupdate: Optional[dt.datetime] = None
    model_config = ConfigDict(extra='ignore')

    @field_validator('title', 'subtitle', 'citation', 'publisher', mode='before')
    @classmethod
    def _normalize_text_pub(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        v = v.replace('\r\n', '\n').replace('\r', '\n').replace('\x0d', '\n')
        v = re.sub(r'\n{3,}', '\n\n', v)
        return v.strip()

    @field_validator('url', mode='before')
    @classmethod
    def _empty_url_to_none_pub(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class PublicationPage(BaseModel):
    info: Optional[PageInfo] = None
    records: List[HAMPublication]
