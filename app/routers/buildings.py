from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import Building, BuildingCreate
from app.crud import get_building, get_buildings, create_building

router = APIRouter()

@router.post("/buildings", response_model=Building)
async def create_new_building(building: BuildingCreate, db: Session = Depends(get_db)):
    """Create a new building"""
    return create_building(db=db, building=building)

@router.get("/buildings", response_model=List[Building])
async def read_buildings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all buildings"""
    buildings = get_buildings(db, skip=skip, limit=limit)
    return buildings

@router.get("/buildings/{building_id}", response_model=Building)
async def read_building(building_id: int, db: Session = Depends(get_db)):
    """Get a specific building by ID"""
    db_building = get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return db_building
