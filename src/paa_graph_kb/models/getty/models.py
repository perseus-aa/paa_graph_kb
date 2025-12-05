from __future__ import annotations
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict

# ======================================================
# Getty Object Models (JSON-LD / Linked Art approximation)
# ======================================================

class Identifier(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = Field(default=None, alias="_content")
    label: Optional[str] = Field(default=None, alias="_label")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

class Classification(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    label: Optional[str] = Field(default=None, alias="_label")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

class Name(BaseModel):
    content: Optional[str] = Field(default=None, alias="_content")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

class Dimension(BaseModel):
    content: Optional[str] = Field(default=None, alias="_content")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

class Image(BaseModel):
    id: str
    type: Optional[str] = None
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    label: Optional[str] = Field(default=None, alias="_label")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

class GettyObject(BaseModel):
    """
    Represents a Getty Museum object (Linked Art JSON-LD).
    This is a simplified model focusing on key fields.
    """
    id: str
    type: str
    label: Optional[str] = Field(default=None, alias="_label")
    identified_by: Optional[List[Identifier]] = None
    classified_as: Optional[List[Classification]] = None
    
    # Images are usually linked via 'representation' in Linked Art
    representation: Optional[List[Image]] = None
    
    # Dimensions
    dimension: Optional[List[Dimension]] = None
    
    # Description usually in 'referred_to_by'
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

class GettyPerson(BaseModel):
    """
    Represents a Person in the Getty dataset (Linked Art JSON-LD).
    """
    id: str
    type: str
    label: Optional[str] = Field(default=None, alias="_label")
    identified_by: Optional[List[Identifier]] = None
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')

