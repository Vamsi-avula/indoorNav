from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.schemas import Fingerprint, FingerprintCreate, FingerprintBatch, RadioMap
from app.crud import (
    get_fingerprint, 
    get_fingerprints_by_floor, 
    create_fingerprint, 
    create_fingerprints_batch,
    get_radiomap
)

router = APIRouter()

@router.post("/fingerprints", response_model=Fingerprint)
async def create_new_fingerprint(fingerprint: FingerprintCreate, db: Session = Depends(get_db)):
    """Create a new fingerprint"""
    return create_fingerprint(db=db, fingerprint=fingerprint)

@router.post("/fingerprints/batch", response_model=List[Fingerprint])
async def create_fingerprint_batch(batch: FingerprintBatch, db: Session = Depends(get_db)):
    """Create multiple fingerprints in a batch"""
    return create_fingerprints_batch(db=db, fingerprints=batch.fingerprints)

@router.get("/fingerprints/{fingerprint_id}", response_model=Fingerprint)
async def read_fingerprint(fingerprint_id: int, db: Session = Depends(get_db)):
    """Get a specific fingerprint by ID"""
    db_fingerprint = get_fingerprint(db, fingerprint_id=fingerprint_id)
    if db_fingerprint is None:
        raise HTTPException(status_code=404, detail="Fingerprint not found")
    return db_fingerprint

@router.get("/floors/{floor_id}/fingerprints", response_model=List[Fingerprint])
async def read_floor_fingerprints(
    floor_id: int, 
    skip: int = 0, 
    limit: int = 1000, 
    db: Session = Depends(get_db)
):
    """Get all fingerprints for a floor"""
    fingerprints = get_fingerprints_by_floor(db, floor_id=floor_id, skip=skip, limit=limit)
    return fingerprints

@router.get("/floors/{floor_id}/radiomap", response_model=RadioMap)
async def get_floor_radiomap(floor_id: int, db: Session = Depends(get_db)):
    """Get radio map for Wi-Fi fingerprinting localization"""
    radio_points = get_radiomap(db, floor_id=floor_id)
    
    return RadioMap(
        floor_id=floor_id,
        points=radio_points
    )

@router.delete("/floors/{floor_id}/fingerprints")
async def clear_floor_fingerprints(floor_id: int, db: Session = Depends(get_db)):
    """Clear all fingerprints for a floor (useful for resurvey)"""
    from app.models import Fingerprint
    
    deleted_count = db.query(Fingerprint).filter(Fingerprint.floor_id == floor_id).delete()
    db.commit()
    
    return {"message": f"Deleted {deleted_count} fingerprints from floor {floor_id}"}
