from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import buildings, floors, fingerprints, upload
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Indoor Navigation API",
    description="Backend for indoor navigation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(buildings.router, prefix="/api/v1", tags=["buildings"])
app.include_router(floors.router, prefix="/api/v1", tags=["floors"])
app.include_router(fingerprints.router, prefix="/api/v1", tags=["fingerprints"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Indoor Navigation API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
