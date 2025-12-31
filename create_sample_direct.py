#!/usr/bin/env python3
"""
Create sample data using direct database access
"""

import sqlite3
import os

def create_sample_data_direct():
    """Create sample data directly in SQLite database"""
    
    # Database path
    db_path = "indoor_navigation.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    print("Creating sample data directly in database...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sample buildings
        buildings_data = [
            (1, "Main Office Building", "123 Business Street, Tech City", "Primary corporate office building", "2024-01-01", "2024-01-01"),
            (2, "Research Center", "456 Innovation Drive, Science Park", "Advanced research and development facility", "2024-01-01", "2024-01-01"),
            (3, "Warehouse Facility", "789 Industrial Road, Logistics Park", "Main storage and distribution center", "2024-01-01", "2024-01-01")
        ]
        
        # Insert buildings
        for building in buildings_data:
            cursor.execute("""
                INSERT OR IGNORE INTO buildings 
                (id, name, address, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, building)
        
        # Sample floors
        floors_data = []
        building_ids = [1, 2, 3]
        
        for building_id in building_ids:
            floor_number = 1
            floors_data.extend([
                (len(floors_data) + 1, building_id, floor_number, "Ground Floor", f"Ground floor of building {building_id}", "2024-01-01", "2024-01-01"),
                (len(floors_data) + 2, building_id, floor_number + 1, "Second Floor", f"Second floor of building {building_id}", "2024-01-01", "2024-01-01"),
                (len(floors_data) + 3, building_id, floor_number + 2, "Third Floor", f"Third floor of building {building_id}", "2024-01-01", "2024-01-01"),
                (len(floors_data) + 4, building_id, floor_number + 3, "Fourth Floor", f"Fourth floor of building {building_id}", "2024-01-01", "2024-01-01")
            ])
            floor_number += 4
        
        # Insert floors
        for floor in floors_data:
            cursor.execute("""
                INSERT OR IGNORE INTO floors 
                (id, building_id, floor_number, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, floor)
        
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM buildings")
        buildings_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM floors")
        floors_count = cursor.fetchone()[0]
        
        print(f"Successfully created sample data:")
        print(f"- {buildings_count} buildings")
        print(f"- {floors_count} floors")
        
        # Show the data
        cursor.execute("SELECT id, name FROM buildings")
        buildings = cursor.fetchall()
        print("\nBuildings:")
        for building in buildings:
            print(f"  {building[0]}: {building[1]}")
        
        cursor.execute("SELECT id, building_id, name FROM floors")
        floors = cursor.fetchall()
        print("\nFloors:")
        for floor in floors:
            print(f"  {floor[0]}: Building {floor[1]} - {floor[2]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_sample_data_direct()
    
    print("\nNext steps:")
    print("1. Restart the server or wait for deployment")
    print("2. Open: https://indoornav-n74i.onrender.com/static/floor_plan_upload.html")
    print("3. Select building and floor from dropdowns")
    print("4. Upload a floor plan image")
