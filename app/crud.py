from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Building, Floor, Fingerprint, AccessPoint
from app.schemas import BuildingCreate, FloorCreate, FingerprintCreate
from typing import List, Optional

# Building CRUD
def get_building(db: Session, building_id: int):
    return db.query(Building).filter(Building.id == building_id).first()

def get_buildings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Building).offset(skip).limit(limit).all()

def create_building(db: Session, building: BuildingCreate):
    db_building = Building(**building.dict())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

# Floor CRUD
def get_floor(db: Session, floor_id: int):
    return db.query(Floor).filter(Floor.id == floor_id).first()

def get_floors_by_building(db: Session, building_id: int):
    return db.query(Floor).filter(Floor.building_id == building_id).all()

def create_floor(db: Session, floor: FloorCreate):
    db_floor = Floor(**floor.dict())
    db.add(db_floor)
    db.commit()
    db.refresh(db_floor)
    return db_floor

# Fingerprint CRUD
def get_fingerprint(db: Session, fingerprint_id: int):
    return db.query(Fingerprint).filter(Fingerprint.id == fingerprint_id).first()

def get_fingerprints_by_floor(db: Session, floor_id: int, skip: int = 0, limit: int = 1000):
    return db.query(Fingerprint).filter(Fingerprint.floor_id == floor_id).offset(skip).limit(limit).all()

def create_fingerprint(db: Session, fingerprint: FingerprintCreate):
    # Convert wifi_scans to dict format for JSON storage
    fingerprint_data = fingerprint.dict()
    wifi_scans = [{"bssid": scan["bssid"], "rssi": scan["rssi"]} for scan in fingerprint_data["wifi_scans"]]
    fingerprint_data["wifi_scans"] = wifi_scans
    
    db_fingerprint = Fingerprint(**fingerprint_data)
    db.add(db_fingerprint)
    
    # Update or create access points
    for scan in wifi_scans:
        ap = db.query(AccessPoint).filter(AccessPoint.bssid == scan["bssid"]).first()
        if ap:
            ap.last_seen = func.now()
        else:
            ap = AccessPoint(bssid=scan["bssid"])
            db.add(ap)
    
    db.commit()
    db.refresh(db_fingerprint)
    return db_fingerprint

def create_fingerprints_batch(db: Session, fingerprints: List[FingerprintCreate]):
    db_fingerprints = []
    for fingerprint in fingerprints:
        db_fingerprint = create_fingerprint(db, fingerprint)
        db_fingerprints.append(db_fingerprint)
    return db_fingerprints

# Radio map for localization
def get_radiomap(db: Session, floor_id: int):
    fingerprints = get_fingerprints_by_floor(db, floor_id)
    return [
        {
            "x": fp.x,
            "y": fp.y,
            "wifi_scans": fp.wifi_scans
        }
        for fp in fingerprints
    ]

# Access Point CRUD
def get_access_points(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(AccessPoint).offset(skip).limit(limit).all()
