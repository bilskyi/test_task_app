from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class TravelProject(Base):
    __tablename__ = 'travel_projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date)
    completed = Column(Boolean, default=False)

    places = relationship('ProjectPlace', back_populates='project', cascade="all, delete-orphan")


class ProjectPlace(Base):
    __tablename__ = 'project_places'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('travel_projects.id'), nullable=False)
    external_place_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    notes = Column(String)
    visited = Column(Boolean, default=False)

    project = relationship('TravelProject', back_populates='places')

    __table_args__ = (
        UniqueConstraint('project_id', 'external_place_id', name='unique_project_place'),
    )