from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine, Base
from app.routes import projects, places

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
    description="A RESTful API for managing travel projects and places to visit",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(places.router)

@app.get("/", tags=["root"])
def read_root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Travel Planner API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health", tags=["root"])
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}