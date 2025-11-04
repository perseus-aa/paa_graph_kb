"""
Geonames vocabulary mappings for HAM place data.

This module provides mappings from HAM place names to Geonames URIs.
Also includes Getty TGN (Thesaurus of Geographic Names) mappings for historical places.

All Geonames IDs are from geonames.org
All TGN IDs are from vocab.getty.edu/tgn/
"""

from typing import Dict, Optional, Tuple

# Place mappings: (geonames_id, tgn_id)
# Some historical places may only have TGN, modern places may only have Geonames
PLACES: Dict[str, Tuple[Optional[str], Optional[str]]] = {
    # Ancient Greece
    "athens": ("264371", "7001393"),  # Athens, Greece
    "sparta": ("253656", "7011086"),  # Sparta, Greece
    "corinth": ("258463", "7010958"),  # Corinth, Greece
    "delphi": ("257707", "7010752"),  # Delphi, Greece
    "olympia": ("253184", "7011093"),  # Olympia, Greece
    "thebes": ("253122", "7012065"),  # Thebes, Greece (Thiva)
    "mycenae": (None, "7011160"),  # Mycenae (ancient site, no modern Geonames)
    "crete": ("261380", "7002939"),  # Crete (island)
    "rhodes": ("250832", "7011175"),  # Rhodes
    "cyprus": ("146669", "7002727"),  # Cyprus

    # Ancient Rome and Italy
    "rome": ("3169070", "7000874"),  # Rome, Italy
    "pompeii": (None, "7004658"),  # Pompeii (archaeological site)
    "herculaneum": (None, "7697629"),  # Herculaneum
    "florence": ("3176959", "7000457"),  # Florence, Italy
    "venice": ("3164603", "7018159"),  # Venice, Italy
    "naples": ("3172394", "7004474"),  # Naples, Italy
    "milan": ("3173435", "7005903"),  # Milan, Italy
    "sicily": ("2523119", "1000080"),  # Sicily

    # Ancient Near East
    "babylon": (None, "7001315"),  # Babylon (ancient)
    "ur": (None, "7001387"),  # Ur (ancient)
    "nineveh": (None, "7001377"),  # Nineveh (ancient)
    "persepolis": (None, "7001867"),  # Persepolis (ancient)
    "baghdad": ("98182", "7001352"),  # Baghdad, Iraq
    "damascus": ("170654", "7001948"),  # Damascus, Syria
    "jerusalem": ("281184", "7001371"),  # Jerusalem
    "antioch": (None, "7002330"),  # Antioch (ancient)

    # Egypt
    "egypt": ("357994", "7016833"),  # Egypt (country)
    "cairo": ("360630", "7001380"),  # Cairo
    "alexandria": ("361058", "7001188"),  # Alexandria
    "thebes": (None, "7001528"),  # Thebes, Egypt (ancient Luxor)
    "luxor": ("360502", "7001528"),  # Luxor (modern Thebes)
    "memphis": (None, "7001468"),  # Memphis, Egypt (ancient)
    "giza": ("360995", "7016659"),  # Giza

    # China
    "china": ("1814991", "1000111"),  # China
    "beijing": ("1816670", "7013297"),  # Beijing
    "shanghai": ("1796236", "8570792"),  # Shanghai
    "xi'an": ("1790437", "8520437"),  # Xi'an (ancient Chang'an)
    "nanjing": ("1799962", "8602901"),  # Nanjing

    # Japan
    "japan": ("1861060", "1000093"),  # Japan
    "tokyo": ("1850147", "7012305"),  # Tokyo
    "kyoto": ("1857910", "7013164"),  # Kyoto
    "nara": ("1855612", "7013155"),  # Nara

    # India
    "india": ("1269750", "7001535"),  # India
    "delhi": ("1273294", "7001534"),  # Delhi
    "mumbai": ("1275339", "7001519"),  # Mumbai (Bombay)
    "agra": ("1279259", "7511886"),  # Agra

    # Western Europe
    "paris": ("2988507", "7008038"),  # Paris, France
    "london": ("2643743", "7011781"),  # London, UK
    "berlin": ("2950159", "7003712"),  # Berlin, Germany
    "madrid": ("3117735", "7007436"),  # Madrid, Spain
    "amsterdam": ("2759794", "7006952"),  # Amsterdam, Netherlands
    "brussels": ("2800866", "7007393"),  # Brussels, Belgium
    "vienna": ("2761369", "7003321"),  # Vienna, Austria

    # Americas
    "new york": ("5128581", "7007567"),  # New York City
    "boston": ("4930956", "7013445"),  # Boston
    "mexico city": ("3530597", "7007477"),  # Mexico City
    "teotihuacan": (None, "7010926"),  # Teotihuacan (ancient)
    "cuzco": ("3941584", "7017771"),  # Cuzco (Cusco), Peru
    "machu picchu": (None, "7017759"),  # Machu Picchu

    # Modern countries (for broader context)
    "france": ("3017382", "1000070"),  # France
    "germany": ("2921044", "7003670"),  # Germany
    "italy": ("3175395", "1000080"),  # Italy
    "spain": ("2510769", "1000095"),  # Spain
    "netherlands": ("2750405", "7016845"),  # Netherlands
    "united kingdom": ("2635167", "7008591"),  # United Kingdom
    "united states": ("6252001", "7012149"),  # United States
    "greece": ("390903", "1000074"),  # Greece (modern)
}


def get_geonames_uri(place: str) -> Optional[str]:
    """
    Look up Geonames URI for a given place name.

    Args:
        place: The place name to look up (case-insensitive)

    Returns:
        Full Geonames URI if found, None otherwise
    """
    if not place:
        return None

    place_lower = place.lower().strip()

    if place_lower in PLACES:
        geonames_id, _ = PLACES[place_lower]
        if geonames_id:
            return f"https://sws.geonames.org/{geonames_id}/"

    # Try partial match
    for key, (geonames_id, _) in PLACES.items():
        if place_lower in key or key in place_lower:
            if geonames_id:
                return f"https://sws.geonames.org/{geonames_id}/"

    return None


def get_tgn_uri(place: str) -> Optional[str]:
    """
    Look up Getty TGN (Thesaurus of Geographic Names) URI for a given place name.

    Args:
        place: The place name to look up (case-insensitive)

    Returns:
        Full TGN URI if found, None otherwise
    """
    if not place:
        return None

    place_lower = place.lower().strip()

    if place_lower in PLACES:
        _, tgn_id = PLACES[place_lower]
        if tgn_id:
            return f"http://vocab.getty.edu/tgn/{tgn_id}"

    # Try partial match
    for key, (_, tgn_id) in PLACES.items():
        if place_lower in key or key in place_lower:
            if tgn_id:
                return f"http://vocab.getty.edu/tgn/{tgn_id}"

    return None


def get_place_authorities(place: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Look up both Geonames and TGN URIs for a given place name.

    Args:
        place: The place name to look up (case-insensitive)

    Returns:
        Tuple of (geonames_uri, tgn_uri), either may be None
    """
    geonames_uri = get_geonames_uri(place)
    tgn_uri = get_tgn_uri(place)
    return (geonames_uri, tgn_uri)


def get_geonames_id(place: str) -> Optional[str]:
    """
    Look up Geonames ID (numeric part only) for a given place name.

    Args:
        place: The place name to look up (case-insensitive)

    Returns:
        Geonames ID (e.g., "264371") if found, None otherwise
    """
    if not place:
        return None

    place_lower = place.lower().strip()

    if place_lower in PLACES:
        geonames_id, _ = PLACES[place_lower]
        return geonames_id

    # Try partial match
    for key, (geonames_id, _) in PLACES.items():
        if place_lower in key or key in place_lower:
            return geonames_id

    return None


def get_tgn_id(place: str) -> Optional[str]:
    """
    Look up TGN ID (numeric part only) for a given place name.

    Args:
        place: The place name to look up (case-insensitive)

    Returns:
        TGN ID (e.g., "7001393") if found, None otherwise
    """
    if not place:
        return None

    place_lower = place.lower().strip()

    if place_lower in PLACES:
        _, tgn_id = PLACES[place_lower]
        return tgn_id

    # Try partial match
    for key, (_, tgn_id) in PLACES.items():
        if place_lower in key or key in place_lower:
            return tgn_id

    return None
