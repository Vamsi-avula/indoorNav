#!/usr/bin/env python3
"""
IndoorNav Data Upload Script
Uploads buildings and POIs to the backend
"""

import json
import requests
from typing import List, Dict, Any

API_BASE = "http://localhost:8000/api/v1"

def upload_building(building_data: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a single building"""
    try:
        response = requests.post(f"{API_BASE}/buildings", json=building_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading building: {e}")
        return None

def upload_poi(poi_data: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a single POI"""
    try:
        response = requests.post(f"{API_BASE}/pois", json=poi_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading POI: {e}")
        return None

def upload_sample_data():
    """Upload sample building and POI data"""
    
    # Sample building
    building = {
        "name": "Engineering Building",
        "address": "123 Tech Street, Campus",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "floors": [
            {"name": "Ground Floor", "number": 0, "width": 100.0, "height": 80.0},
            {"name": "First Floor", "number": 1, "width": 100.0, "height": 80.0},
            {"name": "Second Floor", "number": 2, "width": 100.0, "height": 80.0}
        ]
    }
    
    print("Uploading building...")
    building_result = upload_building(building)
    if building_result:
        print(f"Building uploaded successfully! ID: {building_result['id']}")
        building_id = building_result['id']
        
        # Sample POIs for each floor
        pois = [
            # Ground Floor POIs
            {"name": "Main Entrance", "description": "Main entrance to building", 
             "latitude": 40.7128, "longitude": -74.0060, "floor_id": 1, "category": "entrance"},
            {"name": "Reception", "description": "Main reception desk", 
             "latitude": 40.7129, "longitude": -74.0061, "floor_id": 1, "category": "other"},
            {"name": "Elevator", "description": "Main elevator", 
             "latitude": 40.7130, "longitude": -74.0062, "floor_id": 1, "category": "elevator"},
            
            # First Floor POIs
            {"name": "Lecture Hall 101", "description": "Large lecture hall", 
             "latitude": 40.7128, "longitude": -74.0060, "floor_id": 2, "category": "room"},
            {"name": "Computer Lab", "description": "Student computer lab", 
             "latitude": 40.7129, "longitude": -74.0061, "floor_id": 2, "category": "room"},
            {"name": "Restroom", "description": "Men's restroom", 
             "latitude": 40.7130, "longitude": -74.0062, "floor_id": 2, "category": "restroom"},
            
            # Second Floor POIs
            {"name": "Faculty Office 201", "description": "Professor Smith's office", 
             "latitude": 40.7128, "longitude": -74.0060, "floor_id": 3, "category": "room"},
            {"name": "Library", "description": "Engineering library", 
             "latitude": 40.7129, "longitude": -74.0061, "floor_id": 3, "category": "room"},
            {"name": "Stairs", "description": "Emergency stairs", 
             "latitude": 40.7130, "longitude": -74.0062, "floor_id": 3, "category": "stairs"}
        ]
        
        print("Uploading POIs...")
        for poi in pois:
            poi_result = upload_poi(poi)
            if poi_result:
                print(f"POI '{poi['name']}' uploaded successfully! ID: {poi_result['id']}")
            else:
                print(f"Failed to upload POI: {poi['name']}")
    
    print("Upload completed!")

def upload_from_json_file(filepath: str):
    """Upload data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Upload buildings
        if 'buildings' in data:
            print(f"Uploading {len(data['buildings'])} buildings...")
            for building in data['buildings']:
                result = upload_building(building)
                if result:
                    print(f"Building '{building['name']}' uploaded successfully!")
        
        # Upload POIs
        if 'pois' in data:
            print(f"Uploading {len(data['pois'])} POIs...")
            for poi in data['pois']:
                result = upload_poi(poi)
                if result:
                    print(f"POI '{poi['name']}' uploaded successfully!")
        
        print("Bulk upload completed!")
        
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {filepath}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Upload from file
        upload_from_json_file(sys.argv[1])
    else:
        # Upload sample data
        upload_sample_data()
