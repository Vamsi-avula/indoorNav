from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from PIL import Image
import io

from app.database import get_db
from app.models import Building, Floor

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads/floor_plans"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-floor-plan/{building_id}/{floor_id}")
async def upload_floor_plan(
    building_id: int,
    floor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a floor plan image for a specific building floor"""
    
    # Verify building and floor exist
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    floor = db.query(Floor).filter(Floor.id == floor_id, Floor.building_id == building_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    unique_filename = f"{building_id}_{floor_id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save and process image
    try:
        # Read image data
        image_data = await file.read()
        
        # Open with PIL to validate and potentially resize
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (max 2048x2048)
        max_size = 2048
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save processed image
        image.save(file_path, 'JPEG', quality=85)
        
        # Update floor record with image path
        floor.floor_plan_image = f"/uploads/floor_plans/{unique_filename}"
        db.commit()
        
        return {
            "message": "Floor plan uploaded successfully",
            "filename": unique_filename,
            "path": floor.floor_plan_image,
            "size": os.path.getsize(file_path)
        }
        
    except Exception as e:
        # Clean up file if upload failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@router.get("/floor-plan/{building_id}/{floor_id}")
async def get_floor_plan(building_id: int, floor_id: int, db: Session = Depends(get_db)):
    """Get floor plan image path for a specific building floor"""
    
    floor = db.query(Floor).filter(Floor.id == floor_id, Floor.building_id == building_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    if not floor.floor_plan_image:
        raise HTTPException(status_code=404, detail="No floor plan uploaded")
    
    return {
        "floor_id": floor_id,
        "building_id": building_id,
        "image_path": floor.floor_plan_image,
        "floor_name": floor.name,
        "floor_number": floor.number
    }

@router.delete("/floor-plan/{building_id}/{floor_id}")
async def delete_floor_plan(building_id: int, floor_id: int, db: Session = Depends(get_db)):
    """Delete a floor plan image"""
    
    floor = db.query(Floor).filter(Floor.id == floor_id, Floor.building_id == building_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    if floor.floor_plan_image:
        # Delete file from filesystem
        file_path = floor.floor_plan_image.replace("/uploads/floor_plans/", UPLOAD_DIR + os.sep)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Clear database reference
        floor.floor_plan_image = None
        db.commit()
    
    return {"message": "Floor plan deleted successfully"}
