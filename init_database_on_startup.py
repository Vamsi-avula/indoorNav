#!/usr/bin/env python3
"""
Initialize database with sample data on startup
This script runs when the app starts to ensure data exists
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, SessionLocal, test_database_connection
from app.models import Building, Floor, Base

def initialize_database():
    """Initialize database with sample data if empty"""
    
    print("🔄 Initializing database...")
    
    # Test database connection
    if not test_database_connection():
        print("❌ Database connection failed")
        return False
    
    # Create tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Check if data exists
    db = SessionLocal()
    try:
        building_count = db.query(Building).count()
        floor_count = db.query(Floor).count()
        
        print(f"📊 Current data: {building_count} buildings, {floor_count} floors")
        
        if building_count == 0:
            print("🏗️ Creating sample data...")
            
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
            
            # Verify creation
            building_count = db.query(Building).count()
            floor_count = db.query(Floor).count()
            
            print(f"✅ Database initialized: {building_count} buildings, {floor_count} floors")
            
            return True
        else:
            print("✅ Database already contains data")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = initialize_database()
    if success:
        print("🎯 Database ready for use!")
    else:
        print("❌ Database initialization failed")
        sys.exit(1)
