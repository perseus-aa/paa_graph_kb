"""
AAT (Getty Art & Architecture Thesaurus) vocabulary mappings for HAM data.

This module provides mappings from HAM vocabulary terms to Getty AAT URIs.
Mappings are organized by category: cultures, materials, techniques, object types, etc.

All AAT IDs are from vocab.getty.edu/aat/
"""

from typing import Dict, Optional

# Culture mappings
CULTURES: Dict[str, str] = {
    # Ancient Mediterranean
    "greek": "300386130",  # Greek (culture or style)
    "roman": "300220890",  # Roman (ancient Italian culture or period)
    "etruscan": "300389007",  # Etruscan (culture or period)
    "egyptian": "300020251",  # Egyptian (ancient)
    "mesopotamian": "300019278",  # Mesopotamian
    "phoenician": "300020174",  # Phoenician
    "cypriot": "300020207",  # Cypriot

    # Asian cultures
    "chinese": "300018322",  # Chinese (culture or style)
    "japanese": "300018295",  # Japanese (culture or style)
    "korean": "300387317",  # Korean (culture or style)
    "indian": "300018863",  # Indian (South Asian)
    "persian": "300020305",  # Persian
    "tibetan": "300018175",  # Tibetan

    # European cultures
    "italian": "300111198",  # Italian (culture or style)
    "french": "300111188",  # French (culture or style)
    "german": "300111192",  # German (culture or style)
    "dutch": "300020929",  # Dutch (culture or style)
    "flemish": "300111158",  # Flemish (culture or style)
    "spanish": "300111215",  # Spanish (culture or style)
    "british": "300111159",  # British (culture or style)
    "english": "300111159",  # English (culture or style) - same as British

    # American cultures
    "american": "300107956",  # American (North American)
    "native american": "300107957",  # Native American
    "mesoamerican": "300017825",  # Mesoamerican
    "andean": "300016480",  # Andean

    # African cultures
    "african": "300411894",  # African (general)
    "egyptian": "300020251",  # Egyptian (ancient)
}

# Material mappings
MATERIALS: Dict[str, str] = {
    # Stone
    "marble": "300011443",  # marble (rock)
    "limestone": "300011286",  # limestone
    "granite": "300011224",  # granite
    "sandstone": "300011452",  # sandstone
    "basalt": "300011158",  # basalt
    "alabaster": "300011130",  # alabaster

    # Metals
    "bronze": "300010957",  # bronze (metal)
    "copper": "300011020",  # copper (metal)
    "gold": "300011021",  # gold (metal)
    "silver": "300011029",  # silver (metal)
    "iron": "300011002",  # iron (metal)
    "lead": "300011025",  # lead (metal)
    "tin": "300011018",  # tin (metal)

    # Clay and ceramics
    "terracotta": "300010669",  # terracotta (material)
    "clay": "300010439",  # clay
    "ceramic": "300010657",  # ceramic (material)
    "porcelain": "300010662",  # porcelain
    "faience": "300010698",  # faience
    "earthenware": "300140803",  # earthenware
    "stoneware": "300140807",  # stoneware

    # Organic materials
    "wood": "300011914",  # wood (plant material)
    "ivory": "300011857",  # ivory
    "bone": "300011798",  # bone (material)
    "shell": "300011829",  # shell (animal material)
    "leather": "300011845",  # leather
    "parchment": "300011851",  # parchment
    "paper": "300014109",  # paper (fiber product)
    "textile": "300014063",  # textile (material)
    "silk": "300243428",  # silk (fiber)
    "wool": "300243430",  # wool (hair material)
    "cotton": "300243429",  # cotton (fiber)
    "linen": "300014069",  # linen (material)

    # Glass
    "glass": "300010797",  # glass (material)

    # Paint and pigments
    "oil paint": "300015050",  # oil paint
    "tempera": "300015062",  # tempera
    "watercolor": "300015045",  # watercolor paint
    "ink": "300015012",  # ink
    "pigment": "300010957",  # pigment
}

# Technique mappings
TECHNIQUES: Dict[str, str] = {
    # Pottery techniques
    "black glaze": "300404385",  # black-glaze (technique)
    "red figure": "300252548",  # red-figure (pottery style)
    "black figure": "300252547",  # black-figure (pottery style)
    "wheel thrown": "300053141",  # throwing (pottery technique)
    "hand built": "300053143",  # handbuilding (technique)
    "slip": "300191948",  # slip (coating)

    # Metalworking
    "casting": "300053104",  # casting (process)
    "forging": "300054058",  # forging (metalworking)
    "engraving": "300053225",  # engraving (printing process)
    "chasing": "300053839",  # chasing (metalworking)
    "repoussé": "300054031",  # repoussé (technique)
    "gilding": "300053789",  # gilding

    # Painting techniques
    "oil painting": "300054216",  # oil painting (technique)
    "fresco": "300053358",  # fresco (technique)
    "tempera painting": "300054379",  # tempera painting
    "watercolor painting": "300054227",  # watercolor painting (technique)
    "drawing": "300033973",  # drawing (image-making)

    # Sculpture techniques
    "carving": "300053149",  # carving (processes)
    "modeling": "300053147",  # modeling (forming)
    "assemblage": "300047896",  # assemblage (sculpture technique)

    # Printmaking
    "etching": "300053225",  # etching (printing process)
    "woodcut": "300041405",  # woodcuts (prints)
    "lithography": "300041379",  # lithography
    "engraving": "300053225",  # engraving

    # Textile techniques
    "weaving": "300053643",  # weaving (process)
    "embroidery": "300264024",  # embroidery (needlework)
    "tapestry": "300205002",  # tapestries (visual works)
    "dyeing": "300054023",  # dyeing
}

# Object type / work type mappings
OBJECT_TYPES: Dict[str, str] = {
    # Pottery and vessels
    "vessel": "300193015",  # vessels (containers)
    "vase": "300132254",  # vases
    "jar": "300045611",  # jars
    "bowl": "300203596",  # bowls (vessels)
    "cup": "300043202",  # cups (vessels)
    "kylix": "300198842",  # kylikes
    "amphora": "300148696",  # amphorae
    "krater": "300198855",  # kraters
    "hydria": "300198903",  # hydriai
    "oinochoe": "300199042",  # oinochoai
    "lekythos": "300198850",  # lekythoi
    "pyxis": "300198929",  # pyxides

    # Sculpture
    "sculpture": "300047090",  # sculpture (visual works)
    "statue": "300047600",  # statues
    "relief": "300047230",  # reliefs (sculptures)
    "bust": "300047625",  # busts (sculpture)
    "statuette": "300189808",  # statuettes
    "figurine": "300189808",  # figurines

    # Painting
    "painting": "300033618",  # paintings (visual works)
    "portrait": "300015637",  # portraits
    "landscape": "300015636",  # landscapes (representations)
    "still life": "300015638",  # still lifes

    # Decorative arts
    "furniture": "300037680",  # furniture
    "jewelry": "300209286",  # jewelry
    "textile": "300014063",  # textiles
    "coin": "300037222",  # coins (money)
    "medal": "300046025",  # medals

    # Works on paper
    "drawing": "300033973",  # drawings (visual works)
    "print": "300041273",  # prints (visual works)
    "manuscript": "300028569",  # manuscripts (documents)
    "book": "300028051",  # books

    # Architectural elements
    "column": "300001571",  # columns (architectural elements)
    "capital": "300001662",  # capitals (column components)
    "frieze": "300009426",  # friezes (ornamental areas)
    "sarcophagus": "300005947",  # sarcophagi
}

# Classification mappings (broader categories)
CLASSIFICATIONS: Dict[str, str] = {
    "vessels": "300193015",  # vessels
    "sculpture": "300047090",  # sculpture
    "paintings": "300033618",  # paintings
    "drawings": "300033973",  # drawings
    "prints": "300041273",  # prints
    "photographs": "300046300",  # photographs
    "decorative arts": "300054168",  # decorative arts
    "furniture": "300037680",  # furniture
    "textiles": "300014063",  # textiles
    "jewelry": "300209286",  # jewelry
    "arms and armor": "300036754",  # arms and armor
    "musical instruments": "300041620",  # musical instruments
    "coins": "300037222",  # coins
    "medals": "300046025",  # medals
    "manuscripts": "300028569",  # manuscripts
    "books": "300028051",  # books
}


def get_aat_uri(term: str, category: str = "all") -> Optional[str]:
    """
    Look up AAT URI for a given term.

    Args:
        term: The term to look up (case-insensitive)
        category: Category to search in (cultures, materials, techniques, object_types, classifications, all)

    Returns:
        Full AAT URI if found, None otherwise
    """
    if not term:
        return None

    term_lower = term.lower().strip()

    # Define search order
    if category == "cultures":
        categories = [CULTURES]
    elif category == "materials":
        categories = [MATERIALS]
    elif category == "techniques":
        categories = [TECHNIQUES]
    elif category == "object_types":
        categories = [OBJECT_TYPES]
    elif category == "classifications":
        categories = [CLASSIFICATIONS]
    else:  # all
        categories = [OBJECT_TYPES, MATERIALS, TECHNIQUES, CULTURES, CLASSIFICATIONS]

    for cat_dict in categories:
        if term_lower in cat_dict:
            aat_id = cat_dict[term_lower]
            return f"http://vocab.getty.edu/aat/{aat_id}"

    # Try partial match (contains)
    for cat_dict in categories:
        for key, aat_id in cat_dict.items():
            if term_lower in key or key in term_lower:
                return f"http://vocab.getty.edu/aat/{aat_id}"

    return None


def get_aat_id(term: str, category: str = "all") -> Optional[str]:
    """
    Look up AAT ID (numeric part only) for a given term.

    Args:
        term: The term to look up (case-insensitive)
        category: Category to search in

    Returns:
        AAT ID (e.g., "300386130") if found, None otherwise
    """
    uri = get_aat_uri(term, category)
    if uri:
        return uri.split("/")[-1]
    return None
