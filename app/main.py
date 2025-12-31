from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import buildings, floors, fingerprints, upload, init, debug, upload_debug
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Try to import map authoring components safely
try:
    # Test database connection first
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    # If database works, try importing map models
    from app.routers import map_authoring
    from app.map_models import FloorPlanVersion, PointOfInterest, RoutingNode, RoutingEdge, MapPublishing
    
    # Create map authoring tables
    try:
        FloorPlanVersion.metadata.create_all(bind=engine)
        PointOfInterest.metadata.create_all(bind=engine)
        RoutingNode.metadata.create_all(bind=engine)
        RoutingEdge.metadata.create_all(bind=engine)
        MapPublishing.metadata.create_all(bind=engine)
        
        MAP_AUTH_ENABLED = True
        print("Map authoring module loaded successfully")
    except Exception as e:
        print(f"Error creating map authoring tables: {e}")
        MAP_AUTH_ENABLED = False
        
except ImportError as e:
    print(f"Map authoring module not available: {e}")
    MAP_AUTH_ENABLED = False
except Exception as e:
    print(f"Error loading map authoring module: {e}")
    MAP_AUTH_ENABLED = False

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
app.include_router(init.router, prefix="/api/v1", tags=["init"])
app.include_router(debug.router, prefix="/api/v1", tags=["debug"])
app.include_router(upload_debug.router, prefix="/api/v1", tags=["upload-debug"])

# Include map authoring router only if enabled
if MAP_AUTH_ENABLED:
    app.include_router(map_authoring.router, prefix="/api/v1", tags=["map-authoring"])

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Indoor Navigation API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
