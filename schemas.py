from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date

class PlaceBase(BaseModel):
    external_place_id: int = Field(..., description="ID from Art Institute API")
    notes: Optional[str] = Field(None, description="User notes about the place")

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    notes: Optional[str] = Field(None, description="Updated notes")
    visited: Optional[bool] = Field(None, description="Mark as visited")

class PlaceInDB(BaseModel):
    id: int
    project_id: int
    external_place_id: int
    title: str
    notes: Optional[str] = None
    visited: bool = False

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    start_date: Optional[date] = Field(None, description="Project start date")

class ProjectCreate(ProjectBase):
    places: Optional[List[PlaceCreate]] = Field(default=[], description="List of places to add (max 10)")
    
    @field_validator('places')
    @classmethod
    def validate_places_count(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 places allowed per project')
        return v

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectInDB(ProjectBase):
    id: int
    completed: bool = False
    places: List[PlaceInDB] = []

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    total: int
    projects: List[ProjectInDB]

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None