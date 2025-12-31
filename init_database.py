#!/usr/bin/env python3
"""
Initialize database with sample data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Building, Floor
from app.database import DATABASE_URL

def init_database():
    """Initialize database with sample data"""
    
    print(f"Using database: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_buildings = db.query(Building).count()
        existing_floors = db.query(Floor).count()
        
        print(f"Existing data: {existing_buildings} buildings, {existing_floors} floors")
        
        if existing_buildings > 0 and existing_floors > 0:
            print("Sample data already exists!")
            return
        
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
        
        print("Creating sample buildings...")
        for building in buildings_data:
            db.add(building)
        
        db.commit()
        
        # Refresh to get IDs
        db.refresh(buildings_data[0])
        db.refresh(buildings_data[1])
        db.refresh(buildings_data[2])
        
        # Create sample floors
        floors_data = []
        floor_templates = [
            (1, "Ground Floor"),
            (2, "Second Floor"),
            (3, "Third Floor"),
            (4, "Fourth Floor")
        ]
        
        print("Creating sample floors...")
        for building in buildings_data:
            for floor_num, floor_name in floor_templates:
                floor = Floor(
                    building_id=building.id,
                    floor_number=floor_num,
                    name=floor_name,
                    description=f"{floor_name} of {building.name}"
                )
                floors_data.append(floor)
                db.add(floor)
        
        db.commit()
        
        # Verify data
        total_buildings = db.query(Building).count()
        total_floors = db.query(Floor).count()
        
        print(f"\n✅ Sample data created successfully!")
        print(f"📊 Summary: {total_buildings} buildings, {total_floors} floors")
        
        # Show the data
        buildings = db.query(Building).all()
        print("\n🏢 Buildings:")
        for building in buildings:
            print(f"  {building.id}: {building.name}")
        
        floors = db.query(Floor).all()
        print("\n🏗️ Floors:")
        for floor in floors:
            print(f"  {floor.id}: Building {floor.building_id} - {floor.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    
    print("\n🎯 Next steps:")
    print("1. Open: https://indoornav-n74i.onrender.com/static/floor_plan_upload.html")
    print("2. The dropdowns should now show buildings and floors")
    print("3. Select a building and floor")
    print("4. Upload your floor plan image")
