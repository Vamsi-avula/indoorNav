from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Building, Floor

router = APIRouter()

@router.post("/init-sample-data")
async def init_sample_data(db: Session = Depends(get_db)):
    """Initialize sample data for testing"""
    
    try:
        # Check if data already exists
        existing_buildings = db.query(Building).count()
        existing_floors = db.query(Floor).count()
        
        if existing_buildings > 0 and existing_floors > 0:
            return {
                "message": "Sample data already exists",
                "buildings": existing_buildings,
                "floors": existing_floors
            }
        
        # Create sample buildings
        buildings_data = [
            Building(
                name="Main Office Building",
                address="123 Business Street, Tech City",
                description="Primary corporate office building"
            ),
            Building(
                name="Research Center",
                address="456 Innovation Drive, Science Park", 
                description="Advanced research and development facility"
            ),
            Building(
                name="Warehouse Facility",
                address="789 Industrial Road, Logistics Park",
                description="Main storage and distribution center"
            )
        ]
        
        for building in buildings_data:
            db.add(building)
        
        db.commit()
        
        # Refresh to get IDs
        for building in buildings_data:
            db.refresh(building)
        
        # Create sample floors
        floor_templates = [
            (1, "Ground Floor"),
            (2, "Second Floor"),
            (3, "Third Floor"),
            (4, "Fourth Floor")
        ]
        
        for building in buildings_data:
            for floor_num, floor_name in floor_templates:
                floor = Floor(
                    building_id=building.id,
                    floor_number=floor_num,
                    name=floor_name,
                    description=f"{floor_name} of {building.name}"
                )
                db.add(floor)
        
        db.commit()
        
        # Get final counts
        total_buildings = db.query(Building).count()
        total_floors = db.query(Floor).count()
        
        return {
            "message": "Sample data created successfully",
            "buildings": total_buildings,
            "floors": total_floors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create sample data: {str(e)}")
