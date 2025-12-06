"""
Perseus staging loader - converts Perseus JSON object data to RDF staging format.

This loader handles Perseus Digital Library's classical artifact metadata,
including rich iconographic descriptions, attribution data, and bibliographic references.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Optional

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

STG = Namespace("https://aa.perseus.org/staging#")
EXS = Namespace("https://aa.perseus.org/staging/")
PERSEUS = Namespace("http://perseus.tufts.edu/ns/aa/")


def _safe_lang_literal(text: str) -> Literal:
    """Create language-tagged literal, defaulting to English for ASCII text."""
    if text and all(ord(ch) < 128 for ch in text):
        return Literal(text, lang="en")
    return Literal(text)


def extract_institution_from_name(name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract institution and accession number from Perseus name field.

    Examples:
        "Harvard 1960.250" → ("Harvard", "1960.250")
        "Cleveland 82.142" → ("Cleveland", "82.142")
        "Malibu 86.AE.34" → ("Malibu", "86.AE.34")
        "Boston 99.345" → ("Boston", "99.345")

    Returns:
        Tuple of (institution_name, accession_number)
    """
    if not name:
        return (None, None)

    # Common institution patterns
    patterns = [
        (r'^Harvard\s+(.+)$', 'Harvard Art Museums'),
        (r'^HAM\s+(.+)$', 'Harvard Art Museums'),
        (r'^H\s+(.+)$', 'Harvard Art Museums'),
        (r'^Cleveland\s+(.+)$', 'Cleveland Museum of Art'),
        (r'^Malibu\s+(.+)$', 'J. Paul Getty Museum'),
        (r'^Boston\s+(.+)$', 'Museum of Fine Arts, Boston'),
        (r'^New\s+York\s+(.+)$', 'Metropolitan Museum of Art'),
        (r'^MMA\s+(.+)$', 'Metropolitan Museum of Art'),
        (r'^London\s+(.+)$', 'British Museum'),
        (r'^BM\s+(.+)$', 'British Museum'),
        (r'^Louvre\s+(.+)$', 'Musée du Louvre'),
        (r'^Athens\s+(.+)$', 'National Archaeological Museum, Athens'),
    ]

    for pattern, institution in patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            accession = match.group(1).strip()
            return (institution, accession)

    # If no pattern matches, try to split on first whitespace
    parts = name.split(None, 1)
    if len(parts) == 2:
        return (parts[0], parts[1])

    return (None, name)


def perseus_object_to_staging(g: Graph, obj: dict[str, Any], source: str = "perseus") -> None:
    """
    Convert a Perseus object record to staging graph triples.

    Args:
        g: RDF graph to add triples to
        obj: Perseus object as dictionary
        source: Source identifier (default: "perseus")
    """
    perseus_id = obj.get("id")
    if not perseus_id:
        return

    # Create staging node
    sid = f"o/{source}:{perseus_id}"
    s = EXS[sid]
    g.add((s, RDF.type, STG.PerseusObject))
    g.add((s, STG.source, Literal(source)))
    g.add((s, STG.perseusId, Literal(perseus_id)))

    # Store original Perseus ID for reference
    g.add((s, PERSEUS.id, Literal(perseus_id)))

    # Name field - extract institution and accession
    name = obj.get("name")
    if name:
        g.add((s, STG.perseusName, Literal(name)))
        institution, accession = extract_institution_from_name(name)
        if institution:
            g.add((s, STG.institution, Literal(institution)))
        if accession:
            g.add((s, STG.accessionNumber, Literal(accession)))

    # Object type
    obj_type = obj.get("type")
    if obj_type:
        g.add((s, STG.objectType, Literal(obj_type)))

    # Location (where Perseus has it stored)
    location = obj.get("location")
    if location:
        g.add((s, STG.location, Literal(location)))

    # Summary
    summary = obj.get("summary")
    if summary:
        g.add((s, STG.summary, _safe_lang_literal(summary)))

    # Perseus version (data quality indicator)
    perseus_version = obj.get("perseus_version")
    if perseus_version:
        g.add((s, STG.perseusVersion, Literal(perseus_version)))

    # Data entry attribution
    entered_by = obj.get("entered_by")
    if entered_by:
        g.add((s, STG.enteredBy, Literal(entered_by)))

    # Sources/Bibliography - preserve TEI markup
    sources_used = obj.get("sources_used")
    if sources_used:
        g.add((s, STG.sourcesUsed, Literal(sources_used)))
        # Create a clean version for display/search
        clean_sources = re.sub(r'<[^>]+>', '', sources_used)
        g.add((s, STG.sourcesUsedClean, Literal(clean_sources)))

    # Dimensions - may contain HTML tags
    dimensions = obj.get("dimensions")
    if dimensions:
        g.add((s, STG.dimensions, Literal(dimensions)))

    # Geographic context
    region = obj.get("region")
    if region:
        g.add((s, STG.region, Literal(region)))

    context = obj.get("context")
    if context:
        g.add((s, STG.context, Literal(context)))

    # Dating information
    start_date = obj.get("start_date")
    if start_date:
        try:
            date_int = int(start_date)
            g.add((s, STG.datebegin, Literal(date_int, datatype=XSD.integer)))
        except (ValueError, TypeError):
            g.add((s, STG.datebegin, Literal(start_date)))

    end_date = obj.get("end_date")
    if end_date:
        try:
            date_int = int(end_date)
            g.add((s, STG.dateend, Literal(date_int, datatype=XSD.integer)))
        except (ValueError, TypeError):
            g.add((s, STG.dateend, Literal(end_date)))

    # Date modifiers (ca., before, after, etc.)
    start_mod = obj.get("start_mod")
    if start_mod:
        g.add((s, STG.startModifier, Literal(start_mod)))

    end_mod = obj.get("end_mod")
    if end_mod:
        g.add((s, STG.endModifier, Literal(end_mod)))

    # Sort date (for chronological ordering)
    date_for_sort = obj.get("date_for_sort")
    if date_for_sort:
        try:
            sort_int = int(date_for_sort)
            g.add((s, STG.dateForSort, Literal(sort_int, datatype=XSD.integer)))
        except (ValueError, TypeError):
            g.add((s, STG.dateForSort, Literal(date_for_sort)))

    # Unitary date (single date value)
    unitary_date = obj.get("unitary_date")
    if unitary_date:
        try:
            date_int = int(unitary_date)
            g.add((s, STG.unitaryDate, Literal(date_int, datatype=XSD.integer)))
        except (ValueError, TypeError):
            g.add((s, STG.unitaryDate, Literal(unitary_date)))

    unitary_mod = obj.get("unitary_mod")
    if unitary_mod:
        g.add((s, STG.unitaryModifier, Literal(unitary_mod)))

    # Period
    period = obj.get("period")
    if period:
        g.add((s, STG.periodLabel, _safe_lang_literal(period)))

    # Collection
    collection = obj.get("collection")
    if collection:
        g.add((s, STG.collection, Literal(collection)))

    # Condition
    condit = obj.get("condit")
    if condit:
        g.add((s, STG.condition, Literal(condit)))

    # Iconographic description - may be very long with embedded line breaks
    decoration_description = obj.get("decoration_description")
    if decoration_description:
        g.add((s, STG.decorationDescription, Literal(decoration_description)))

    # Shape
    shape = obj.get("shape")
    if shape:
        g.add((s, STG.shape, _safe_lang_literal(shape)))

    # Ware
    ware = obj.get("ware")
    if ware:
        g.add((s, STG.ware, _safe_lang_literal(ware)))

    # Attribution information
    painter = obj.get("painter")
    if painter:
        g.add((s, STG.painter, Literal(painter)))

    painter_mod = obj.get("painter_mod")
    if painter_mod:
        g.add((s, STG.painterModifier, Literal(painter_mod)))

    # Beazley Archive number (key identifier for Greek vases)
    beazley_number = obj.get("beazley_number")
    if beazley_number:
        g.add((s, STG.beazleyNumber, Literal(beazley_number)))


def perseus_image_to_staging(g: Graph, img: dict[str, Any], source: str = "perseus") -> URIRef:
    """
    Convert a Perseus image record to staging graph triples.

    Args:
        g: RDF graph to add triples to
        img: Perseus image as dictionary
        source: Source identifier (default: "perseus")

    Returns:
        URIRef of the created image node
    """
    image_id = img.get("id")
    if not image_id:
        raise ValueError("Image record missing required 'id' field")

    # Create image node
    img_node = URIRef(f"https://aa.perseus.org/staging/image/{image_id}")
    g.add((img_node, RDF.type, STG.PerseusImage))
    g.add((img_node, STG.source, Literal(source)))
    g.add((img_node, STG.imageId, Literal(image_id)))

    # Archive number (preferred identifier)
    archive_number = img.get("archive_number")
    if archive_number:
        g.add((img_node, STG.archiveNumber, Literal(archive_number)))

    # Name(s) - may be a list
    names = img.get("name")
    if names:
        if isinstance(names, list):
            for name in names:
                g.add((img_node, STG.imageName, Literal(name)))
        else:
            g.add((img_node, STG.imageName, Literal(names)))

    # Caption
    caption = img.get("caption")
    if caption:
        g.add((img_node, STG.caption, _safe_lang_literal(caption)))

    # Credits/attribution
    credits = img.get("credits")
    if credits:
        g.add((img_node, STG.credits, Literal(credits)))

    # IIIF service (constructed from ID)
    # Perseus uses: https://iiif.perseus.tufts.edu/iiif/3/{id}
    iiif_base = f"https://iiif.perseus.tufts.edu/iiif/3/{image_id}"
    g.add((img_node, STG.iiifImageService, URIRef(iiif_base)))

    return img_node


def main() -> None:
    """Main entry point for Perseus staging loader."""
    ap = argparse.ArgumentParser(
        description="Load Perseus object data from JSON and emit staging RDF triples."
    )
    ap.add_argument(
        "--objects",
        type=Path,
        help="Path to Perseus objects JSON file",
    )
    ap.add_argument(
        "--images",
        type=Path,
        help="Path to Perseus images JSON file",
    )
    ap.add_argument(
        "--out-objects",
        type=Path,
        help="Output path for objects staging TTL (required if --objects provided)",
    )
    ap.add_argument(
        "--out-images",
        type=Path,
        help="Output path for images staging TTL (required if --images provided)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        help="Limit number of records to process (for testing)",
    )

    args = ap.parse_args()

    # Validate arguments
    if not args.objects and not args.images:
        print("❌ Error: Must provide at least one of --objects or --images")
        ap.print_help()
        exit(1)

    if args.objects and not args.out_objects:
        print("❌ Error: --out-objects required when --objects is provided")
        exit(1)

    if args.images and not args.out_images:
        print("❌ Error: --out-images required when --images is provided")
        exit(1)

    # Process objects
    if args.objects:
        print(f"📖 Loading Perseus objects from {args.objects}")

        with open(args.objects, 'r', encoding='utf-8') as f:
            objects = json.load(f)

        if not isinstance(objects, list):
            print("❌ Error: Expected JSON array of objects")
            exit(1)

        g = Graph()
        g.bind("stg", STG)
        g.bind("exs", EXS)
        g.bind("perseus", PERSEUS)

        count = 0
        limit = args.limit or len(objects)

        for obj in objects[:limit]:
            try:
                perseus_object_to_staging(g, obj, source="perseus")
                count += 1
                if count % 100 == 0:
                    print(f"   Processed {count} objects...")
            except Exception as e:
                obj_id = obj.get("id", "unknown")
                print(f"⚠️  Warning: Failed to process object {obj_id}: {e}")
                continue

        g.serialize(destination=args.out_objects, format="turtle")
        print(f"✅ Wrote {count} objects and {len(g)} triples to {args.out_objects}")

    # Process images
    if args.images:
        print(f"📸 Loading Perseus images from {args.images}")

        with open(args.images, 'r', encoding='utf-8') as f:
            images = json.load(f)

        if not isinstance(images, list):
            print("❌ Error: Expected JSON array of images")
            exit(1)

        g = Graph()
        g.bind("stg", STG)
        g.bind("exs", EXS)

        count = 0
        limit = args.limit or len(images)

        for img in images[:limit]:
            try:
                perseus_image_to_staging(g, img, source="perseus")
                count += 1
                if count % 100 == 0:
                    print(f"   Processed {count} images...")
            except Exception as e:
                img_id = img.get("id", "unknown")
                print(f"⚠️  Warning: Failed to process image {img_id}: {e}")
                continue

        g.serialize(destination=args.out_images, format="turtle")
        print(f"✅ Wrote {count} images and {len(g)} triples to {args.out_images}")


if __name__ == "__main__":
    main()
