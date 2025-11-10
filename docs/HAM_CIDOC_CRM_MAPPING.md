# HAM API to CIDOC-CRM Mapping Table

## Legend
- ✅ = Fully mapped to CIDOC-CRM
- ⚠️ = Partially mapped or could be improved
- ❌ = Not currently mapped
- 🔍 = Captured in staging but not transformed to CRM

## Object Core Fields

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `objectid` | `stg:objectid` | 01+ (all) | Used to generate object URI | ✅ |
| `objectnumber` | `stg:objectnumber` | 09 | `crm:E42_Identifier` → `crm:P190_has_symbolic_content` | ✅ |
| `standardreferencenumber` | `stg:standardreferencenumber` | 09 | `crm:E42_Identifier` → `crm:P190_has_symbolic_content` | ✅ |
| `title` | `stg:title` | 01 | `rdfs:label` + `crm:E33_E41_Linguistic_Appellation` | ✅ |
| `titles[]` | `stg:title` (multiple) | 01 | `crm:E33_E41_Linguistic_Appellation` | ✅ |
| `url` | `stg:catalogPage` | 05 | `la:digitally_carried_by` → `crm:D1_Digital_Object` | ✅ |

## Classification & Typing

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `worktypes[].worktype` | `stg:typeLabel` + `stg:aatType` | 01 | `crm:P2_has_type` → AAT URI with `rdfs:label` | ✅ |
| `classification` | `stg:typeLabel` + `stg:aatType` | 01, 11 | `crm:P2_has_type` → AAT URI + `crm:E55_Type` with label | ✅ |
| `culture` | `stg:culture` + `stg:cultureAAT` | 01 | `crm:P2_has_type` → AAT URI with `rdfs:label` | ✅ |
| `style` | `stg:style` | 11 | `crm:P2_has_type` → `crm:E55_Type` with label | ✅ |

## Materials & Techniques

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `medium` | `stg:material` + `stg:materialAAT` | 03 | `crm:P45_consists_of` → AAT URI with `rdfs:label` | ✅ |
| `technique` | `stg:technique` + `stg:techniqueAAT` | 04 | `crm:P32_used_general_technique` → AAT URI with `rdfs:label` | ✅ |

## Dating & Chronology

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `datebegin` | `stg:datebegin` | 10 | `crm:E52_Time-Span` → `crm:P82a_begin_of_the_begin` | ✅ |
| `dateend` | `stg:dateend` | 10 | `crm:E52_Time-Span` → `crm:P82b_end_of_the_end` | ✅ |
| `dated` | `stg:dated` | 10 | `rdfs:label` on timespan | ✅ |
| `century` | `stg:century` | - | - | 🔍 |
| `period` | `stg:periodLabel` | 02 | `crm:E4_Period` with `rdfs:label` | ✅ |
| `periodid` | `stg:periodId` | 02 | Used to generate period URI | ✅ |

## Production Context

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `people[].personid` | `stg:personid` | 16, 17 | `crm:E21_Person` | ✅ |
| `people[].name` | `stg:personName` | 16 | `crm:E33_E41_Linguistic_Appellation` | ✅ |
| `people[].displayname` | `stg:personDisplayName` | 16 | `crm:P190_has_symbolic_content` | ✅ |
| `people[].role` | `stg:personRole` | 17 | `crm:PC14_carried_out_by` → `crm:P14.1_in_the_role_of` | ✅ |
| `people[].culture` | `stg:personCulture` | 16 | `crm:E55_Type` with label | ✅ |
| `people[].birthplace` | `stg:personBirthPlace` | 16 | `crm:E67_Birth` → `crm:P7_took_place_at` → `crm:E53_Place` | ✅ |
| `people[].deathplace` | `stg:personDeathPlace` | 16 | `crm:E69_Death` → `crm:P7_took_place_at` → `crm:E53_Place` | ✅ |
| `people[].displaydate` | `stg:personDisplayDate` | 16 | Captured but not in CRM | 🔍 |

## Person Enrichment (from /person endpoint)

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `alphasort` | `stg:personAlphaSort` | 16 | `crm:E33_E41_Linguistic_Appellation` (sort name) | ✅ |
| `gender` | `stg:personGender` | 16 | `crm:P2_has_type` → `crm:E55_Type` | ✅ |
| `birthyear` | `stg:personBirthYear` | 16 | `crm:E67_Birth` → `crm:E52_Time-Span` → `crm:P82a_begin_of_the_begin` | ✅ |
| `deathyear` | `stg:personDeathYear` | 16 | `crm:E69_Death` → `crm:E52_Time-Span` → `crm:P82a_begin_of_the_begin` | ✅ |
| `datebegin` | `stg:personDateBegin` | 16 | Captured but not in CRM | 🔍 |
| `dateend` | `stg:personDateEnd` | 16 | Captured but not in CRM | 🔍 |
| `lcnaf_id` | `stg:lcnafId` | 16 | `owl:sameAs` → LCNAF URI | ✅ |
| `ulan_id` | `stg:ulanId` | 16 | `owl:sameAs` → Getty ULAN URI | ✅ |
| `viaf_id` | `stg:viafId` | 16 | `owl:sameAs` → VIAF URI | ✅ |
| `wikidata_id` | `stg:wikidataId` | 16 | `owl:sameAs` → Wikidata URI | ✅ |
| `wikipedia_id` | `stg:wikipediaId` | 16 | `owl:sameAs` → Wikipedia URI | ✅ |

## Textual Descriptions

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `description` | `stg:description` | 08 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `commentary` | `stg:commentary` | 08 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `labeltext` | `stg:labeltext` | 08 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `provenance` | `stg:provenance` | 06 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `creditline` | `stg:creditline` | 06 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `dimensions` | `stg:dimensions` | 07 | `crm:P43_has_dimension` → `crm:E54_Dimension` | ✅ |
| `signed` | - | - | - | ❌ |
| `state` | - | - | - | ❌ |
| `edition` | - | - | - | ❌ |

## Institutional Data

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `department` | `stg:department` | 12 | `crm:P46_is_composed_of` → `crm:E78_Curated_Holding` | ✅ |
| `division` | `stg:division` | 12 | `crm:P46_is_composed_of` → `crm:E78_Curated_Holding` | ✅ |
| `accessionyear` | `stg:accessionyear` | 14 | `crm:E10_Transfer_of_Custody` → `crm:E52_Time-Span` | ✅ |
| `accessionmethod` | `stg:accessionmethod` | 14 | `crm:E10_Transfer_of_Custody` → `crm:P2_has_type` | ✅ |
| `contact` | - | - | - | ❌ |

## Visual Representations

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `primaryimageurl` | `stg:primaryImage` | 05 | `la:digitally_shown_by` → `crm:D1_Digital_Object` | ✅ |
| `seeAlso[].id` (IIIF) | `stg:iiifManifest` | 05 | `la:digitally_shown_by` → `crm:D1_Digital_Object` | ✅ |
| `images[].imageid` | `stg:imageid` | 15 | Used to generate image URI | ✅ |
| `images[].baseimageurl` | `stg:baseImageURL` | 15 | `crm:D1_Digital_Object` (subject) | ✅ |
| `images[].iiifbaseuri` | `stg:iiifBaseURI` | 15 | `la:access_point` | ✅ |
| `images[].width` | `stg:imageWidth` | 15 | `crm:P43_has_dimension` → `crm:E54_Dimension` | ✅ |
| `images[].height` | `stg:imageHeight` | 15 | `crm:P43_has_dimension` → `crm:E54_Dimension` | ✅ |
| `images[].format` | `stg:imageFormat` | 15 | `crm:P2_has_type` → `crm:E55_Type` | ✅ |
| `images[].description` | `stg:imageDescription` | 15 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `images[].alttext` | `stg:altText` | 15 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `images[].publiccaption` | `stg:publicCaption` | 15 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `images[].copyright` | `stg:copyright` | 15 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `images[].technique` | `stg:imageTechnique` | - | - | 🔍 |
| `images[].renditionnumber` | `stg:renditionNumber` | - | - | 🔍 |
| `images[].displayorder` | `stg:displayOrder` | - | - | 🔍 |
| `images[].date` | `stg:imageDate` | - | - | 🔍 |

## Colors

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `colors[].color` | `stg:colorName` | 13 | `crm:E55_Type` with `rdfs:label` | ✅ |
| `colors[].spectrum` | `stg:hexValue` | 13 | `crm:P190_has_symbolic_content` (hex color) | ✅ |
| `colors[].hue` | - | - | - | ❌ |
| `colors[].percent` | - | - | - | ❌ |
| `colors[].css3` | - | - | - | ❌ |

## Publications (from /publication endpoint)

| HAM Field | Staging Property | Template | CIDOC-CRM Pattern | Status |
|-----------|------------------|----------|-------------------|--------|
| `id` | `stg:publicationid` | 18 | Used to generate publication URI | ✅ |
| `title` | `stg:publicationTitle` | 18 | `crm:P1_is_identified_by` → `crm:E33_E41_Linguistic_Appellation` | ✅ |
| `subtitle` | `stg:publicationSubtitle` | 18 | `crm:P1_is_identified_by` → `crm:E33_E41_Linguistic_Appellation` | ✅ |
| `citation` | `stg:publicationCitation` | 18 | `crm:P67i_is_referred_to_by` → `crm:E33_Linguistic_Object` | ✅ |
| `authors[]` | `stg:publicationAuthor` | 18 | `crm:P94i_was_created_by` → `crm:E65_Creation` → `crm:E39_Actor` | ✅ |
| `publishyear` | `stg:publicationYear` | 18 | `crm:P94i_was_created_by` → `crm:E52_Time-Span` | ✅ |
| `publisher` | `stg:publisher` | 18 | `crm:P70i_is_documented_in` → `crm:E74_Group` | ⚠️ |
| `isbn` | `stg:isbn` | 18 | `crm:P1_is_identified_by` → `crm:E42_Identifier` | ✅ |
| `issn` | `stg:issn` | 18 | `crm:P1_is_identified_by` → `crm:E42_Identifier` | ✅ |
| `doi` | `stg:doi` | 18 | `crm:P1_is_identified_by` → `crm:E42_Identifier` (as URI) | ✅ |
| `url` | `stg:publicationURL` | 18 | `la:digitally_carried_by` → `crm:D1_Digital_Object` | ✅ |

## Analytics & Metadata (NOT mapped)

| HAM Field | Captured? | Notes |
|-----------|-----------|-------|
| `imagecount` | ❌ | Could be useful for completeness metrics |
| `mediacount` | ❌ | |
| `colorcount` | ❌ | |
| `markscount` | ❌ | |
| `peoplecount` | ❌ | |
| `titlescount` | ❌ | |
| `publicationcount` | ❌ | |
| `exhibitioncount` | ❌ | No exhibition data currently captured |
| `contextualtextcount` | ❌ | |
| `groupcount` | ❌ | |
| `relatedcount` | ❌ | No related objects currently captured |
| `totalpageviews` | ❌ | Web analytics - not typically in cultural heritage RDF |
| `totaluniquepageviews` | ❌ | |
| `verificationlevel` | ❌ | Quality/confidence score - could be useful |
| `verificationleveldescription` | ❌ | |
| `imagepermissionlevel` | ❌ | Rights management - could be important |
| `lendingpermissionlevel` | ❌ | |
| `accesslevel` | ❌ | Access control - could be important |
| `rank` | ❌ | |
| `createdate` | ❌ | HAM record metadata - not object metadata |
| `lastupdate` | ❌ | |
| `dateoffirstpageview` | ❌ | |
| `dateoflastpageview` | ❌ | |

## Summary Statistics

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Fully mapped | 70 | 69% |
| 🔍 In staging, not CRM | 8 | 8% |
| ❌ Not captured | 23 | 23% |
| **Total HAM fields** | **101** | **100%** |

## Key Gaps & Opportunities

### High Priority (Semantic Loss)
1. **`signed`** - Inscriptions are important for classical art (could use `crm:P128_carries` → `crm:E34_Inscription`)
2. **`state`** - Print/artwork state information
3. **`edition`** - Edition information for multiples
4. **`century`** - Additional temporal information currently lost
5. **`images[].date`** - When photo was taken (useful for condition documentation)

### Medium Priority (Enrichment)
6. **`verificationlevel`** - Could map to confidence/certainty annotations
7. **`imagepermissionlevel`** - Rights management (could use `crm:P104_is_subject_to` → `crm:E30_Right`)
8. **`accesslevel`** - Access restrictions
9. **Person date ranges** - `datebegin`/`dateend` in staging but not in CRM (active period vs. birth/death)

### Low Priority (Display Metadata)
10. **Display orders** - For images, people (useful for UIs but not semantic)
11. **Rendition numbers** - Image versions
12. **Analytics** - Pageviews, counts (operational, not scholarly)
13. **HAM system metadata** - createdate, lastupdate (provenance of record, not object)

## Recommendations

1. **Add inscription support** for `signed` field
2. **Add edition/state support** for prints and multiples
3. **Consider rights management** for `imagepermissionlevel` and `accesslevel`
4. **Add certainty/confidence** annotations for `verificationlevel`
5. **Image dating** for photographic documentation provenance
