import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, Base
from app.models import Building, Floor, Fingerprint
from app.schemas import BuildingCreate, FloorCreate, FingerprintCreate

@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_building_and_floor(client):
    # Create building
    building_data = {"name": "Test Building"}
    building_response = client.post("/api/v1/buildings", json=building_data)
    building_id = building_response.json()["id"]
    
    # Create floor
    floor_data = {
        "building_id": building_id,
        "floor_number": 1,
        "name": "First Floor",
        "width": 50.0,
        "height": 50.0
    }
    floor_response = client.post("/api/v1/floors", json=floor_data)
    floor_id = floor_response.json()["id"]
    
    return building_id, floor_id

def test_create_fingerprint(client, sample_building_and_floor):
    building_id, floor_id = sample_building_and_floor
    
    fingerprint_data = {
        "floor_id": floor_id,
        "x": 10.5,
        "y": 20.3,
        "device_model": "Pixel 7",
        "wifi_scans": [
            {"bssid": "00:11:22:33:44:55", "rssi": -45.0},
            {"bssid": "aa:bb:cc:dd:ee:ff", "rssi": -67.0}
        ]
    }
    
    response = client.post("/api/v1/fingerprints", json=fingerprint_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["x"] == fingerprint_data["x"]
    assert data["y"] == fingerprint_data["y"]
    assert data["floor_id"] == floor_id
    assert len(data["wifi_scans"]) == 2

def test_create_fingerprint_batch(client, sample_building_and_floor):
    building_id, floor_id = sample_building_and_floor
    
    batch_data = {
        "fingerprints": [
            {
                "floor_id": floor_id,
                "x": 10.0,
                "y": 10.0,
                "wifi_scans": [{"bssid": "00:11:22:33:44:55", "rssi": -45.0}]
            },
            {
                "floor_id": floor_id,
                "x": 20.0,
                "y": 20.0,
                "wifi_scans": [{"bssid": "aa:bb:cc:dd:ee:ff", "rssi": -55.0}]
            }
        ]
    }
    
    response = client.post("/api/v1/fingerprints/batch", json=batch_data)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2

def test_get_radiomap(client, sample_building_and_floor):
    building_id, floor_id = sample_building_and_floor
    
    # Create some fingerprints first
    fingerprint_data = {
        "floor_id": floor_id,
        "x": 10.5,
        "y": 20.3,
        "wifi_scans": [{"bssid": "00:11:22:33:44:55", "rssi": -45.0}]
    }
    client.post("/api/v1/fingerprints", json=fingerprint_data)
    
    response = client.get(f"/api/v1/floors/{floor_id}/radiomap")
    assert response.status_code == 200
    
    data = response.json()
    assert data["floor_id"] == floor_id
    assert len(data["points"]) == 1
    assert data["points"][0]["x"] == 10.5
    assert data["points"][0]["y"] == 20.3
