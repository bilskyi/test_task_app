from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import TravelProject, ProjectPlace
from schemas import PlaceCreate, PlaceUpdate, PlaceInDB, MessageResponse
from services.art_institute import art_service

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])

@router.post("/", response_model=PlaceInDB, status_code=201)
async def add_place_to_project(
    project_id: int,
    place: PlaceCreate,
    db: Session = Depends(get_db)
):
    """
    Add a place to an existing project.
    
    - Validates place exists in Art Institute API
    - Enforces maximum 10 places per project
    - Prevents duplicate places in same project
    """
    # Check project exists
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check place count
    place_count = db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id).count()
    if place_count >= 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 places allowed per project"
        )
    
    # Validate place exists in API
    artwork = await art_service.get_artwork(place.external_place_id)
    if not artwork:
        raise HTTPException(
            status_code=404,
            detail=f"Artwork with ID {place.external_place_id} not found in Art Institute API"
        )
    
    # Check for duplicate
    existing = db.query(ProjectPlace).filter(
        ProjectPlace.project_id == project_id,
        ProjectPlace.external_place_id == place.external_place_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Place {place.external_place_id} already exists in this project"
        )
    
    # Create place
    db_place = ProjectPlace(
        project_id=project_id,
        external_place_id=artwork["id"],
        title=artwork["title"],
        notes=place.notes
    )
    
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    
    return db_place

@router.get("/", response_model=List[PlaceInDB])
def list_places(project_id: int, db: Session = Depends(get_db)):
    """
    List all places for a specific project.
    """
    # Check project exists
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    places = db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id).all()
    return places

@router.get("/{place_id}", response_model=PlaceInDB)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    """
    Get a single place within a project.
    """
    place = db.query(ProjectPlace).filter(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id
    ).first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    return place

@router.put("/{place_id}", response_model=PlaceInDB)
def update_place(
    project_id: int,
    place_id: int,
    place_update: PlaceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a place within a project.
    
    - Can update notes
    - Can mark as visited
    - Auto-completes project when all places are visited
    """
    place = db.query(ProjectPlace).filter(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id
    ).first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    # Update fields
    update_data = place_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(place, field, value)
    
    db.commit()
    
    # Check if all places are visited to mark project as completed
    all_places = db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id).all()
    if all_places and all(p.visited for p in all_places):
        project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
        if project:
            project.completed = True
            db.commit()
    else:
        # If any place is not visited, ensure project is not completed
        project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
        if project and project.completed:
            project.completed = False
            db.commit()
    
    db.refresh(place)
    return place

@router.delete("/{place_id}", response_model=MessageResponse)
def delete_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    """
    Delete a place from a project.
    
    Note: This is not explicitly required but added for completeness.
    """
    place = db.query(ProjectPlace).filter(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id
    ).first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    db.delete(place)
    db.commit()
    
    return MessageResponse(message="Place deleted successfully")