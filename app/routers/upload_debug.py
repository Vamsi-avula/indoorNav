from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Floor

router = APIRouter()

@router.get("/debug/floor/{floor_id}")
async def debug_floor_details(floor_id: int, db: Session = Depends(get_db)):
    """Get detailed debug info for a specific floor"""
    
    try:
        # Get floor details
        floor = db.query(Floor).filter(Floor.id == floor_id).first()
        
        if not floor:
            return {
                "error": f"Floor with ID {floor_id} not found",
                "floor_id": floor_id,
                "exists": False
            }
        
        return {
            "floor_id": floor.id,
            "building_id": floor.building_id,
            "name": floor.name,
            "floor_number": floor.floor_number,
            "floor_plan_image": floor.floor_plan_image,
            "image_url": floor.image_url,
            "has_floor_plan_image": bool(floor.floor_plan_image),
            "has_image_url": bool(floor.image_url),
            "created_at": floor.created_at.isoformat() if floor.created_at else None,
            "updated_at": floor.updated_at.isoformat() if floor.updated_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")

@router.post("/debug/test-floor-update/{floor_id}")
async def test_floor_update(floor_id: int, db: Session = Depends(get_db)):
    """Test updating a floor record"""
    
    try:
        # Get floor
        floor = db.query(Floor).filter(Floor.id == floor_id).first()
        
        if not floor:
            return {"error": f"Floor {floor_id} not found"}
        
        # Test update
        test_path = f"/uploads/test_floor_{floor_id}.jpg"
        floor.floor_plan_image = test_path
        db.commit()
        
        # Verify update
        db.refresh(floor)
        
        return {
            "success": True,
            "floor_id": floor.id,
            "test_path_set": floor.floor_plan_image == test_path,
            "current_path": floor.floor_plan_image
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Test update failed: {str(e)}")

@router.post("/debug/clear-floor-image/{floor_id}")
async def clear_floor_image(floor_id: int, db: Session = Depends(get_db)):
    """Clear floor image for testing"""
    
    try:
        # Get floor
        floor = db.query(Floor).filter(Floor.id == floor_id).first()
        
        if not floor:
            return {"error": f"Floor {floor_id} not found"}
        
        # Clear image
        floor.floor_plan_image = None
        db.commit()
        
        return {
            "success": True,
            "floor_id": floor.id,
            "image_cleared": True,
            "current_path": floor.floor_plan_image
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")
