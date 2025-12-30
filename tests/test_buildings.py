import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, Base
from app.models import Building
from app.schemas import BuildingCreate

# Override database for testing
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

def test_create_building(client):
    building_data = {
        "name": "Test Building",
        "address": "123 Test St",
        "description": "A test building"
    }
    
    response = client.post("/api/v1/buildings", json=building_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == building_data["name"]
    assert data["address"] == building_data["address"]
    assert "id" in data

def test_get_buildings(client):
    # Create a building first
    building_data = {"name": "Test Building"}
    client.post("/api/v1/buildings", json=building_data)
    
    response = client.get("/api/v1/buildings")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Building"

def test_get_building(client):
    # Create a building first
    building_data = {"name": "Test Building"}
    create_response = client.post("/api/v1/buildings", json=building_data)
    building_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/buildings/{building_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Test Building"
    assert data["id"] == building_id

def test_get_nonexistent_building(client):
    response = client.get("/api/v1/buildings/999")
    assert response.status_code == 404
