from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import Floor, FloorCreate
from app.crud import get_floor, get_floors_by_building, create_floor

router = APIRouter()

@router.get("/floors", response_model=List[Floor])
async def read_all_floors(db: Session = Depends(get_db)):
    """Get all floors"""
    # This is a simple implementation - you might want to add pagination
    from app.models import Floor as FloorModel
    floors = db.query(FloorModel).all()
    return floors

@router.post("/floors", response_model=Floor)
async def create_new_floor(floor: FloorCreate, db: Session = Depends(get_db)):
    """Create a new floor"""
    return create_floor(db=db, floor=floor)

@router.get("/floors/{floor_id}", response_model=Floor)
async def read_floor(floor_id: int, db: Session = Depends(get_db)):
    """Get a specific floor by ID"""
    db_floor = get_floor(db, floor_id=floor_id)
    if db_floor is None:
        raise HTTPException(status_code=404, detail="Floor not found")
    return db_floor

@router.get("/buildings/{building_id}/floors", response_model=List[Floor])
async def read_building_floors(building_id: int, db: Session = Depends(get_db)):
    """Get all floors for a building"""
    floors = get_floors_by_building(db, building_id=building_id)
    return floors

@router.get("/floors/{floor_id}/graph")
async def get_floor_navigation_graph(floor_id: int, db: Session = Depends(get_db)):
    """Get navigation graph for a floor"""
    db_floor = get_floor(db, floor_id=floor_id)
    if db_floor is None:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    return {
        "floor_id": floor_id,
        "walkable_graph": db_floor.walkable_graph
    }
