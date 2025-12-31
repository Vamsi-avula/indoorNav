from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import Building, Floor

router = APIRouter()

@router.post("/force-create-sample-data")
async def force_create_sample_data(db: Session = Depends(get_db)):
    """Force create sample data - more robust version"""
    
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Clear existing data to avoid conflicts
        db.query(Floor).delete()
        db.query(Building).delete()
        db.commit()
        
        # Create buildings
        buildings = [
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
        
        for building in buildings:
            db.add(building)
        
        db.commit()
        
        # Refresh to get IDs
        for building in buildings:
            db.refresh(building)
        
        # Create floors
        floor_templates = [
            (1, "Ground Floor"),
            (2, "Second Floor"),
            (3, "Third Floor"),
            (4, "Fourth Floor")
        ]
        
        for building in buildings:
            for floor_num, floor_name in floor_templates:
                floor = Floor(
                    building_id=building.id,
                    floor_number=floor_num,
                    name=floor_name
                )
                db.add(floor)
        
        db.commit()
        
        # Get final counts
        total_buildings = db.query(Building).count()
        total_floors = db.query(Floor).count()
        
        return {
            "message": "Sample data force created successfully",
            "buildings": total_buildings,
            "floors": total_floors,
            "data": {
                "buildings": [
                    {"id": b.id, "name": b.name} for b in db.query(Building).all()
                ],
                "floors": [
                    {"id": f.id, "building_id": f.building_id, "name": f.name, "floor_number": f.floor_number} 
                    for f in db.query(Floor).all()
                ]
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create sample data: {str(e)}")

@router.get("/debug/database-status")
async def debug_database_status(db: Session = Depends(get_db)):
    """Debug database status and show all data"""
    
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Get all data
        buildings = db.query(Building).all()
        floors = db.query(Floor).all()
        
        return {
            "database_status": "connected",
            "buildings_count": len(buildings),
            "floors_count": len(floors),
            "buildings": [
                {
                    "id": b.id,
                    "name": b.name,
                    "address": b.address,
                    "description": b.description
                } for b in buildings
            ],
            "floors": [
                {
                    "id": f.id,
                    "building_id": f.building_id,
                    "name": f.name,
                    "floor_number": f.floor_number,
                    "floor_plan_image": f.floor_plan_image
                } for f in floors
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
