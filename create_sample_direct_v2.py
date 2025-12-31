#!/usr/bin/env python3
"""
Simple direct database sample data creation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Building, Floor
from app.database import DATABASE_URL

def create_sample_data_direct():
    """Create sample data directly"""
    
    print(f"Database URL: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check existing data
        existing_buildings = db.query(Building).count()
        existing_floors = db.query(Floor).count()
        
        print(f"Existing data: {existing_buildings} buildings, {existing_floors} floors")
        
        if existing_buildings == 0:
            print("Creating buildings...")
            
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
            
            print(f"Created {len(buildings)} buildings")
            
            # Create floors
            floor_templates = [
                (1, "Ground Floor"),
                (2, "Second Floor"),
                (3, "Third Floor"),
                (4, "Fourth Floor")
            ]
            
            print("Creating floors...")
            for building in buildings:
                for floor_num, floor_name in floor_templates:
                    floor = Floor(
                        building_id=building.id,
                        floor_number=floor_num,
                        name=floor_name
                    )
                    db.add(floor)
            
            db.commit()
            print("Created floors")
        
        # Verify data
        buildings = db.query(Building).all()
        floors = db.query(Floor).all()
        
        print(f"\n✅ Final data:")
        print(f"📊 Buildings: {len(buildings)}")
        print(f"🏗️ Floors: {len(floors)}")
        
        print("\n🏢 Buildings:")
        for building in buildings:
            print(f"  {building.id}: {building.name}")
        
        print("\n🏗️ Floors:")
        for floor in floors:
            print(f"  {floor.id}: Building {floor.building_id} - {floor.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_sample_data_direct()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Open: https://indoornav-n74i.onrender.com/static/floor_plan_debug.html")
        print("2. Click 'Check All Floors' to verify data")
        print("3. Then try uploading your floor plan")
    else:
        print("\n❌ Failed to create sample data")
