"""
Vocabulary mapping modules for authority linking.

This package provides mappings from HAM vocabulary terms to external authorities:
- AAT (Getty Art & Architecture Thesaurus)
- Geonames (geographic authority)
- TGN (Getty Thesaurus of Geographic Names)
"""

from . import aat_mappings, geonames_mappings

__all__ = ["aat_mappings", "geonames_mappings"]
