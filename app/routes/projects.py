from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models.models import TravelProject, ProjectPlace
from app.schemas.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectInDB,
    ProjectListResponse,
    MessageResponse
)
from app.services.art_institute import art_service

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectInDB, status_code=201)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new travel project with optional places.
    
    - Maximum 10 places per project
    - Places are validated against Art Institute API
    """
    # Validate places count
    if project.places and len(project.places) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 places allowed per project")
    
    # Create project
    db_project = TravelProject(
        name=project.name,
        description=project.description,
        start_date=project.start_date
    )
    db.add(db_project)
    db.flush()  # Get project ID without committing
    
    # Add places if provided
    if project.places:
        for place_data in project.places:
            # Validate place exists in API
            artwork = await art_service.get_artwork(place_data.external_place_id)
            if not artwork:
                db.rollback()
                raise HTTPException(
                    status_code=404,
                    detail=f"Artwork with ID {place_data.external_place_id} not found in Art Institute API"
                )
            
            # Check for duplicate
            existing = db.query(ProjectPlace).filter(
                ProjectPlace.project_id == db_project.id,
                ProjectPlace.external_place_id == place_data.external_place_id
            ).first()
            
            if existing:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Place {place_data.external_place_id} already exists in this project"
                )
            
            # Create place
            db_place = ProjectPlace(
                project_id=db_project.id,
                external_place_id=artwork["id"],
                title=artwork["title"],
                notes=place_data.notes
            )
            db.add(db_place)
    
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.get("/", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all travel projects with pagination.
    
    - Default: Returns first 100 projects
    - Use skip and limit for pagination
    """
    total = db.query(TravelProject).count()
    projects = db.query(TravelProject).offset(skip).limit(limit).all()
    
    return ProjectListResponse(total=total, projects=projects)

@router.get("/{project_id}", response_model=ProjectInDB)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get a single project by ID with all its places.
    """
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

@router.put("/{project_id}", response_model=ProjectInDB)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update project information (name, description, start_date).
    """
    db_project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields if provided
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project.
    
    - Cannot delete if any places are marked as visited
    """
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if any places are visited
    visited_places = db.query(ProjectPlace).filter(
        ProjectPlace.project_id == project_id,
        ProjectPlace.visited == True
    ).first()
    
    if visited_places:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete project with visited places"
        )
    
    db.delete(project)
    db.commit()
    
    return MessageResponse(message="Project deleted successfully")