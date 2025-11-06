from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

from paa_graph_kb.clients.ham_client import HAMClient
from paa_graph_kb.models.ham.models import HAMObject, HAMPerson, HAMPublication
from paa_graph_kb.vocabularies import aat_mappings, geonames_mappings

STG = Namespace("https://aa.perseus.org/staging#")
EXS = Namespace("https://aa.perseus.org/staging/")
AAT = "http://vocab.getty.edu/aat/"


def _safe_lang_literal(text: str) -> Literal:
    # best-effort language tagging
    if text and all(ord(ch) < 128 for ch in text):
        return Literal(text, lang="en")
    return Literal(text)


def object_to_staging(g: Graph, obj: HAMObject, source: str = "ham") -> None:
    sid = f"o/{source}:{obj.objectid}"
    s = EXS[sid]
    g.add((s, RDF.type, STG.Object))
    g.add((s, STG.source, Literal(source)))
    g.add((s, STG.objectid, Literal(obj.objectid, datatype=XSD.integer)))

    # Titles
    if obj.title:
        g.add((s, STG.title, _safe_lang_literal(obj.title)))
    if obj.titles:
        for t in obj.titles:
            if t.title:
                g.add((s, STG.title, _safe_lang_literal(t.title)))

    # Culture (with AAT mapping)
    if obj.culture:
        culture_uri = aat_mappings.get_aat_uri(obj.culture, category="cultures")
        if culture_uri:
            g.add((s, STG.cultureAAT, URIRef(culture_uri)))

    # Worktypes (with AAT mapping)
    if obj.worktypes:
        for wt in obj.worktypes:
            if wt.worktype:
                type_uri = aat_mappings.get_aat_uri(wt.worktype, category="object_types")
                if type_uri:
                    g.add((s, STG.aatType, URIRef(type_uri)))

    # Classification (with AAT mapping)
    if obj.classification:
        class_uri = aat_mappings.get_aat_uri(obj.classification, category="classifications")
        if class_uri:
            g.add((s, STG.aatType, URIRef(class_uri)))

    # Materials (with AAT mapping)
    if obj.medium:
        material_uri = aat_mappings.get_aat_uri(obj.medium, category="materials")
        if material_uri:
            g.add((s, STG.materialAAT, URIRef(material_uri)))

    # Techniques (with AAT mapping)
    if obj.technique:
        technique_uri = aat_mappings.get_aat_uri(obj.technique, category="techniques")
        if technique_uri:
            g.add((s, STG.techniqueAAT, URIRef(technique_uri)))

    # Period
    if obj.periodid is not None:
        g.add((s, STG.periodId, Literal(obj.periodid, datatype=XSD.integer)))
    if obj.period:
        g.add((s, STG.periodLabel, _safe_lang_literal(obj.period)))

    # Representations
    if obj.seeAlso:
        for it in obj.seeAlso:
            if it.type and "IIIF" in it.type.upper() and it.id:
                g.add((s, STG.iiifManifest, URIRef(str(it.id))))
    if obj.primaryimageurl:
        g.add((s, STG.primaryImage, URIRef(str(obj.primaryimageurl))))

    # Catalog page
    if obj.url:
        g.add((s, STG.catalogPage, URIRef(str(obj.url))))

    # Notes
    if obj.creditline:
        g.add((s, STG.creditline, Literal(obj.creditline)))
    if obj.provenance:
        g.add((s, STG.provenance, Literal(obj.provenance)))

    # Dimensions
    if obj.dimensions:
        g.add((s, STG.dimensions, Literal(obj.dimensions)))

    # Additional textual descriptions
    if obj.description:
        g.add((s, STG.description, Literal(obj.description)))
    if obj.commentary:
        g.add((s, STG.commentary, Literal(obj.commentary)))
    if obj.labeltext:
        g.add((s, STG.labeltext, Literal(obj.labeltext)))

    # Identifiers
    if obj.objectnumber:
        g.add((s, STG.objectnumber, Literal(obj.objectnumber)))
    if obj.standardreferencenumber:
        g.add((s, STG.standardreferencenumber, Literal(obj.standardreferencenumber)))

    # Dating information
    if obj.datebegin is not None:
        g.add((s, STG.datebegin, Literal(obj.datebegin, datatype=XSD.integer)))
    if obj.dateend is not None:
        g.add((s, STG.dateend, Literal(obj.dateend, datatype=XSD.integer)))
    if obj.dated:
        g.add((s, STG.dated, Literal(obj.dated)))
    if obj.century:
        g.add((s, STG.century, Literal(obj.century)))

    # Classification
    if obj.classification:
        g.add((s, STG.classification, Literal(obj.classification)))
    if obj.style:
        g.add((s, STG.style, Literal(obj.style)))

    # Department/Division
    if obj.department:
        g.add((s, STG.department, Literal(obj.department)))
    if obj.division:
        g.add((s, STG.division, Literal(obj.division)))

    # Colors
    if obj.colors:
        for color in obj.colors:
            if color.color:
                g.add((s, STG.colorName, Literal(color.color)))
                if color.spectrum:
                    # Store hex value as additional property
                    color_bn = URIRef(
                        f"https://aa.perseus.org/staging/color/{obj.objectid}/{color.color}"
                    )
                    g.add((color_bn, STG.hexValue, Literal(color.spectrum)))
                    g.add((s, STG.hasColor, color_bn))

    # Accession information
    if obj.accessionyear is not None:
        g.add((s, STG.accessionyear, Literal(obj.accessionyear, datatype=XSD.integer)))
    if obj.accessionmethod:
        g.add((s, STG.accessionmethod, Literal(obj.accessionmethod)))

    # Image metadata
    if obj.images:
        for img in obj.images:
            if img.imageid:
                # Create image node
                img_node = URIRef(
                    f"https://aa.perseus.org/staging/image/{obj.objectid}/{img.imageid}"
                )
                g.add((s, STG.hasImage, img_node))
                g.add(
                    (img_node, STG.imageid, Literal(img.imageid, datatype=XSD.integer))
                )

                # Image URLs
                if img.baseimageurl:
                    g.add((img_node, STG.baseImageURL, URIRef(str(img.baseimageurl))))
                if img.iiifbaseuri:
                    g.add((img_node, STG.iiifBaseURI, URIRef(str(img.iiifbaseuri))))

                # Image dimensions
                if img.width:
                    g.add(
                        (
                            img_node,
                            STG.imageWidth,
                            Literal(img.width, datatype=XSD.integer),
                        )
                    )
                if img.height:
                    g.add(
                        (
                            img_node,
                            STG.imageHeight,
                            Literal(img.height, datatype=XSD.integer),
                        )
                    )

                # Image format
                if img.format:
                    g.add((img_node, STG.imageFormat, Literal(img.format)))

                # Textual metadata
                if img.description:
                    g.add((img_node, STG.imageDescription, Literal(img.description)))
                if img.alttext:
                    g.add((img_node, STG.altText, Literal(img.alttext)))
                if img.publiccaption:
                    g.add((img_node, STG.publicCaption, Literal(img.publiccaption)))

                # Copyright
                if img.copyright:
                    g.add((img_node, STG.copyright, Literal(img.copyright)))

                # Additional metadata
                if img.technique:
                    g.add((img_node, STG.imageTechnique, Literal(img.technique)))
                if img.renditionnumber:
                    g.add((img_node, STG.renditionNumber, Literal(img.renditionnumber)))
                if img.displayorder is not None:
                    g.add(
                        (
                            img_node,
                            STG.displayOrder,
                            Literal(img.displayorder, datatype=XSD.integer),
                        )
                    )

                # Image date (when the image was created)
                if img.image_date:
                    g.add(
                        (
                            img_node,
                            STG.imageDate,
                            Literal(img.image_date, datatype=XSD.date),
                        )
                    )

    # People/Agents (artists, makers, etc.)
    if obj.people:
        for person in obj.people:
            if person.personid:
                # Create person node
                person_node = URIRef(
                    f"https://aa.perseus.org/staging/person/{person.personid}"
                )
                g.add((s, STG.hasPerson, person_node))
                g.add((person_node, RDF.type, STG.Person))
                g.add(
                    (person_node, STG.personid, Literal(person.personid, datatype=XSD.integer))
                )

                # Person identity
                if person.name:
                    g.add((person_node, STG.personName, Literal(person.name)))
                if person.displayname:
                    g.add((person_node, STG.personDisplayName, Literal(person.displayname)))
                if person.role:
                    g.add((person_node, STG.personRole, Literal(person.role)))
                if person.culture:
                    g.add((person_node, STG.personCulture, Literal(person.culture)))
                if person.displaydate:
                    g.add((person_node, STG.personDisplayDate, Literal(person.displaydate)))

                # Person places
                if person.birthplace:
                    g.add((person_node, STG.personBirthPlace, Literal(person.birthplace)))
                if person.deathplace:
                    g.add((person_node, STG.personDeathPlace, Literal(person.deathplace)))


def enrich_persons_with_authorities(g: Graph, client: HAMClient, limit: Optional[int] = None) -> int:
    """
    Fetch full person records from HAM /person endpoint and add authority IDs to existing person nodes.

    Args:
        g: The RDF graph containing person nodes
        client: HAMClient instance
        limit: Optional limit on number of persons to enrich

    Returns:
        Number of persons enriched with authority data
    """
    # Collect all person IDs from the graph
    person_ids = set()
    for s, p, o in g.triples((None, STG.personid, None)):
        person_ids.add(int(o))

    if not person_ids:
        print(f"No person nodes found in graph to enrich")
        return 0

    enriched = 0
    print(f"Found {len(person_ids)} unique persons in graph, fetching full records...")

    # Fetch full person records for each personid
    for personid in person_ids:
        if limit and enriched >= limit:
            break

        try:
            # Fetch person by ID using the API
            # We'll iterate with a filter on the exact ID
            persons = list(client.iter_people(params={"id": personid}, limit=1))

            if not persons:
                continue

            person = persons[0]
            person_node = URIRef(f"https://aa.perseus.org/staging/person/{personid}")

            # Add additional fields from full person record
            if person.alphasort:
                g.add((person_node, STG.personAlphaSort, Literal(person.alphasort)))
            if person.gender:
                g.add((person_node, STG.personGender, Literal(person.gender)))

            # Add detailed date information
            if person.datebegin is not None:
                g.add((person_node, STG.personDateBegin, Literal(person.datebegin, datatype=XSD.integer)))
            if person.dateend is not None:
                g.add((person_node, STG.personDateEnd, Literal(person.dateend, datatype=XSD.integer)))
            if person.birthyear is not None:
                g.add((person_node, STG.personBirthYear, Literal(person.birthyear, datatype=XSD.integer)))
            if person.deathyear is not None:
                g.add((person_node, STG.personDeathYear, Literal(person.deathyear, datatype=XSD.integer)))

            # Add authority identifiers - these are the key enrichments!
            if person.lcnaf_id:
                # LCNAF URIs: http://id.loc.gov/authorities/names/{id}
                lcnaf_uri = URIRef(f"http://id.loc.gov/authorities/names/{person.lcnaf_id}")
                g.add((person_node, STG.lcnafId, lcnaf_uri))

            if person.ulan_id:
                # ULAN URIs: http://vocab.getty.edu/ulan/{id}
                ulan_uri = URIRef(f"http://vocab.getty.edu/ulan/{person.ulan_id}")
                g.add((person_node, STG.ulanId, ulan_uri))

            if person.viaf_id:
                # VIAF URIs: http://viaf.org/viaf/{id}
                viaf_uri = URIRef(f"http://viaf.org/viaf/{person.viaf_id}")
                g.add((person_node, STG.viafId, viaf_uri))

            if person.wikidata_id:
                # Wikidata URIs: http://www.wikidata.org/entity/{id}
                wikidata_uri = URIRef(f"http://www.wikidata.org/entity/{person.wikidata_id}")
                g.add((person_node, STG.wikidataId, wikidata_uri))

            if person.wikipedia_id:
                # Wikipedia URLs are stored as-is or constructed
                # HAM stores the page title, construct full URL
                # Note: This is a simplification, real Wikipedia IDs might need more careful handling
                wikipedia_uri = URIRef(f"https://en.wikipedia.org/wiki/{person.wikipedia_id.replace(' ', '_')}")
                g.add((person_node, STG.wikipediaId, wikipedia_uri))

            enriched += 1
            if enriched % 10 == 0:
                print(f"  Enriched {enriched}/{len(person_ids)} persons...")

        except Exception as e:
            print(f"Warning: Could not enrich person {personid}: {e}")
            continue

    print(f"✅ Enriched {enriched} persons with authority identifiers")
    return enriched


def publication_to_staging(g: Graph, pub: HAMPublication, source: str = "ham") -> None:
    """
    Convert a HAM publication record to staging graph triples.

    Args:
        g: RDF graph to add triples to
        pub: HAMPublication instance
        source: Source identifier (default: "ham")
    """
    # Publication node URI
    pub_node = URIRef(f"https://aa.perseus.org/staging/publication/{pub.id}")

    # Type and identifier
    g.add((pub_node, RDF.type, STG.Publication))
    g.add((pub_node, STG.publicationid, Literal(pub.id, datatype=XSD.integer)))
    g.add((pub_node, STG.source, Literal(source)))

    # Title information
    if pub.title:
        g.add((pub_node, STG.publicationTitle, Literal(pub.title)))
    if pub.subtitle:
        g.add((pub_node, STG.publicationSubtitle, Literal(pub.subtitle)))
    if pub.citation:
        g.add((pub_node, STG.publicationCitation, Literal(pub.citation)))

    # Authors
    if pub.authors:
        for author in pub.authors:
            if author:
                g.add((pub_node, STG.publicationAuthor, Literal(author)))

    # Publication details
    if pub.publishyear is not None:
        g.add((pub_node, STG.publicationYear, Literal(pub.publishyear, datatype=XSD.integer)))
    if pub.publisher:
        g.add((pub_node, STG.publisher, Literal(pub.publisher)))

    # Identifiers (ISBN, ISSN, DOI)
    if pub.isbn:
        g.add((pub_node, STG.isbn, Literal(pub.isbn)))
    if pub.issn:
        g.add((pub_node, STG.issn, Literal(pub.issn)))
    if pub.doi:
        # DOI as URI
        doi_uri = URIRef(f"https://doi.org/{pub.doi}")
        g.add((pub_node, STG.doi, doi_uri))

    # URL
    if pub.url:
        g.add((pub_node, STG.publicationURL, URIRef(str(pub.url))))


def main() -> None:
    import os

    # Load .env file early
    from dotenv import load_dotenv
    load_dotenv()

    ap = argparse.ArgumentParser(
        description="Load HAM objects via the Pydantic client and emit STAGING triples. "
        "Reads HAM_APIKEY and HAM_API_BASE from .env file by default, "
        "or override with --apikey and --base arguments."
    )
    ap.add_argument("--apikey", help="HAM API key (defaults to HAM_APIKEY from .env)")
    ap.add_argument("--base", help="HAM API base URL (defaults to HAM_API_BASE from .env)")
    ap.add_argument(
        "--params",
        nargs="*",
        default=[],
        help="key=value pairs, e.g., culture=Greek hasimage=1",
    )
    ap.add_argument("--size", type=int, default=100)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument(
        "--enrich-persons",
        action="store_true",
        help="Fetch full person records and add authority IDs (VIAF, ULAN, Wikidata, etc.)",
    )
    args = ap.parse_args()

    # Parse params
    param_dict: dict[str, str] = {}
    for p in args.params:
        if "=" in p:
            k, v = p.split("=", 1)
            param_dict[k] = v
        else:
            param_dict[p] = "1"

    # HAMClient reads from env vars, so set them if provided via args (overriding .env)
    if args.apikey:
        os.environ["HAM_APIKEY"] = args.apikey
    if args.base:
        os.environ["HAM_API_BASE"] = args.base

    # Verify API key is available
    if not os.environ.get("HAM_APIKEY"):
        print("❌ Error: HAM_APIKEY not found.")
        print("   Either set HAM_APIKEY in .env file (copy from dotenv template)")
        print("   or provide --apikey argument")
        exit(1)

    client = HAMClient()
    g = Graph()
    g.bind("stg", STG)
    g.bind("exs", EXS)

    count = 0
    for rec in client.iter_objects(params=param_dict, size=args.size, limit=args.limit):
        object_to_staging(g, rec, source="ham")
        count += 1

    # Optionally enrich person records with authority identifiers
    if args.enrich_persons:
        enriched = enrich_persons_with_authorities(g, client)
        print(f"✅ Added authority links for {enriched} persons")

    g.serialize(destination=args.out, format="turtle")
    print(f"✅ Wrote {count} objects and {len(g)} staging triples to {args.out}")


if __name__ == "__main__":
    main()
