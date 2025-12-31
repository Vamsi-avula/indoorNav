#!/usr/bin/env python3
"""
Simple script to create sample buildings and floors
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
                print(f"Failed to create building: {response.status_code} - {response.text}")
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
                    print(f"Failed to create floor: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error creating floor: {e}")
    
    print(f"\nSample data created successfully!")
    print(f"Summary: {len(created_buildings)} buildings, {len(created_floors)} floors")
    
    return created_buildings, created_floors

def check_server_status():
    """Check if server is running"""
    
    print("Checking server status...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("Server is running!")
            return True
        else:
            print(f"Server returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"Server not accessible: {e}")
        return False

def main():
    """Main function"""
    
    print("Simple Sample Data Creator")
    print("=" * 40)
    
    # Check server status
    if not check_server_status():
        print("Server is not running. Please wait for deployment to complete.")
        return
    
    # Create sample data
    create_sample_data()
    
    print("\nNext steps:")
    print("1. Open: https://indoornav-n74i.onrender.com/static/floor_plan_upload.html")
    print("2. Select a building and floor from dropdowns")
    print("3. Upload a floor plan image")
    print("4. Then try: https://indoornav-n74i.onrender.com/static/map_authoring.html")

if __name__ == "__main__":
    main()
