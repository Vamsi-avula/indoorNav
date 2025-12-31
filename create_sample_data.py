#!/usr/bin/env python3
"""
Create sample data for Map Authoring testing
"""

import requests
import json

# API base URL
API_BASE = "https://indoornav-n74i.onrender.com/api/v1"

def create_sample_data():
    """Create sample buildings and floors"""
    
    print("Creating sample buildings and floors...")
    
    # Sample buildings
    buildings_data = [
        {
            "name": "Main Office Building",
            "address": "123 Business Street, Tech City",
            "description": "Primary corporate office building"
        },
        {
            "name": "Research Center",
            "address": "456 Innovation Drive, Science Park",
            "description": "Advanced research and development facility"
        },
        {
            "name": "Warehouse Facility",
            "address": "789 Industrial Road, Logistics Park",
            "description": "Main storage and distribution center"
        }
    ]
    
    created_buildings = []
    
    # Create buildings
    for building_data in buildings_data:
        try:
            response = requests.post(f"{API_BASE}/buildings/", json=building_data)
            if response.status_code == 200:
                building = response.json()
                created_buildings.append(building)
                print(f"Created building: {building['name']} (ID: {building['id']})")
            else:
                print(f"Failed to create building: {response.text}")
        except Exception as e:
            print(f"Error creating building: {e}")
    
    # Create floors for each building
    floor_data_templates = [
        {"floor_number": 1, "name": "Ground Floor"},
        {"floor_number": 2, "name": "Second Floor"},
        {"floor_number": 3, "name": "Third Floor"},
        {"floor_number": 4, "name": "Fourth Floor"}
    ]
    
    created_floors = []
    
    for building in created_buildings:
        print(f"\nCreating floors for {building['name']}...")
        
        for floor_template in floor_data_templates:
            floor_data = {
                "building_id": building["id"],
                "floor_number": floor_template["floor_number"],
                "name": floor_template["name"],
                "description": f"{floor_template['name']} of {building['name']}"
            }
            
            try:
                response = requests.post(f"{API_BASE}/floors/", json=floor_data)
                if response.status_code == 200:
                    floor = response.json()
                    created_floors.append(floor)
                    print(f"Created floor: {floor['name']} (ID: {floor['id']})")
                else:
                    print(f"Failed to create floor: {response.text}")
            except Exception as e:
                print(f"Error creating floor: {e}")
    
    print(f"\nSample data created successfully!")
    print(f"Summary: {len(created_buildings)} buildings, {len(created_floors)} floors")
    
    return created_buildings, created_floors

def check_existing_data():
    """Check if data already exists"""
    
    print("Checking existing data...")
    
    try:
        # Check buildings
        buildings_response = requests.get(f"{API_BASE}/buildings")
        if buildings_response.status_code == 200:
            buildings = buildings_response.json()
            print(f"Found {len(buildings)} existing buildings")
            
            if buildings:
                print("Existing buildings:")
                for building in buildings:
                    print(f"  - {building['name']} (ID: {building['id']})")
            
            # Check floors
            floors_response = requests.get(f"{API_BASE}/floors")
            if floors_response.status_code == 200:
                floors = floors_response.json()
                print(f"Found {len(floors)} existing floors")
                
                if floors:
                    print("Existing floors:")
                    for floor in floors:
                        print(f"  - {floor['name']} (ID: {floor['id']}, Building: {floor['building_id']})")
            
            return len(buildings) > 0, len(floors) > 0
            
        else:
            print(f"Failed to check existing data: {buildings_response.text}")
            return False, False
            
    except Exception as e:
        print(f"Error checking existing data: {e}")
        return False, False

def main():
    """Main function"""
    
    print("Map Authoring Sample Data Creator")
    print("=" * 50)
    
    # Check if data already exists
    has_buildings, has_floors = check_existing_data()
    
    if has_buildings and has_floors:
        print("\nSample data already exists!")
        
        # Ask user if they want to create more
        response = input("\nDo you want to create additional sample data? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Create sample data
    create_sample_data()
    
    print("\nNext steps:")
    print("1. Open: https://indoornav-n74i.onrender.com/static/map_authoring.html")
    print("2. Go to 'Version Management' tab")
    print("3. Select a building and floor from dropdowns")
    print("4. Upload a floor plan image")
    print("5. Try the POI and routing features!")

if __name__ == "__main__":
    main()
