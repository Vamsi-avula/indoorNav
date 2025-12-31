from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from PIL import Image
import io
import json
from datetime import datetime

from app.database import get_db
from app.models import Building, Floor
from app.map_models import FloorPlanVersion, PointOfInterest, RoutingNode, RoutingEdge, MapPublishing
from app.map_schemas import (
    FloorPlanVersionCreate, FloorPlanVersionUpdate, FloorPlanVersion,
    POICreate, POIUpdate, PointOfInterest,
    RoutingNodeCreate, RoutingNodeUpdate, RoutingNode,
    RoutingEdgeCreate, RoutingEdgeUpdate, RoutingEdge,
    MapPublishingCreate, MapPublishingUpdate, MapPublishing,
    MapValidationResult, MapPublishingWorkflow
)

router = APIRouter()

# Floor Plan Version Management
@router.post("/floors/{floor_id}/versions", response_model=FloorPlanVersion)
async def create_floor_plan_version(
    floor_id: int,
    file: UploadFile = File(...),
    version_number: int = Query(...),
    scale: float = Query(1.0),
    change_notes: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Create a new version of floor plan"""
    
    # Verify floor exists
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    # Check if version number already exists
    existing_version = db.query(FloorPlanVersion).filter(
        FloorPlanVersion.floor_id == floor_id,
        FloorPlanVersion.version_number == version_number
    ).first()
    if existing_version:
        raise HTTPException(status_code=400, detail="Version number already exists")
    
    # Validate file type
    if not file.content_type.startswith('image/') and file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be an image or PDF")
    
    # Create uploads directory
    UPLOAD_DIR = f"uploads/floor_plans/versions/{floor_id}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    unique_filename = f"v{version_number}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Process file
    file_size = 0
    width = None
    height = None
    
    try:
        file_data = await file.read()
        file_size = len(file_data)
        
        if file.content_type == 'application/pdf':
            # Handle PDF files
            with open(file_path, 'wb') as f:
                f.write(file_data)
            file_type = 'pdf'
        else:
            # Handle image files
            image = Image.open(io.BytesIO(file_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            image.save(file_path, 'JPEG', quality=85)
            file_type = 'image'
        
        # Create version record
        version = FloorPlanVersion(
            floor_id=floor_id,
            version_number=version_number,
            file_path=f"/uploads/floor_plans/versions/{floor_id}/{unique_filename}",
            file_type=file_type,
            file_size=file_size,
            width=width,
            height=height,
            scale=scale,
            change_notes=change_notes,
            created_by=created_by,
            is_active=True
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return version
        
    except Exception as e:
        # Clean up file if upload failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.get("/floors/{floor_id}/versions", response_model=List[FloorPlanVersion])
async def get_floor_plan_versions(floor_id: int, db: Session = Depends(get_db)):
    """Get all versions of a floor plan"""
    versions = db.query(FloorPlanVersion).filter(
        FloorPlanVersion.floor_id == floor_id
    ).order_by(FloorPlanVersion.version_number.desc()).all()
    return versions

@router.get("/floors/{floor_id}/versions/{version_id}", response_model=FloorPlanVersion)
async def get_floor_plan_version(floor_id: int, version_id: int, db: Session = Depends(get_db)):
    """Get a specific version of floor plan"""
    version = db.query(FloorPlanVersion).filter(
        FloorPlanVersion.id == version_id,
        FloorPlanVersion.floor_id == floor_id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.put("/floors/{floor_id}/versions/{version_id}", response_model=FloorPlanVersion)
async def update_floor_plan_version(
    floor_id: int, 
    version_id: int,
    version_update: FloorPlanVersionUpdate,
    db: Session = Depends(get_db)
):
    """Update floor plan version metadata"""
    version = db.query(FloorPlanVersion).filter(
        FloorPlanVersion.id == version_id,
        FloorPlanVersion.floor_id == floor_id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    for field, value in version_update.dict(exclude_unset=True).items():
        setattr(version, field, value)
    
    db.commit()
    db.refresh(version)
    return version

# Points of Interest Management
@router.post("/versions/{version_id}/pois", response_model=PointOfInterest)
async def create_poi(poi: POICreate, db: Session = Depends(get_db)):
    """Create a Point of Interest"""
    version = db.query(FloorPlanVersion).filter(FloorPlanVersion.id == poi.version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    db_poi = PointOfInterest(**poi.dict())
    db.add(db_poi)
    db.commit()
    db.refresh(db_poi)
    return db_poi

@router.get("/versions/{version_id}/pois", response_model=List[PointOfInterest])
async def get_pois(version_id: int, db: Session = Depends(get_db)):
    """Get all POIs for a version"""
    pois = db.query(PointOfInterest).filter(
        PointOfInterest.version_id == version_id,
        PointOfInterest.is_active == True
    ).all()
    return pois

@router.put("/pois/{poi_id}", response_model=PointOfInterest)
async def update_poi(poi_id: int, poi_update: POIUpdate, db: Session = Depends(get_db)):
    """Update a Point of Interest"""
    poi = db.query(PointOfInterest).filter(PointOfInterest.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    
    for field, value in poi_update.dict(exclude_unset=True).items():
        setattr(poi, field, value)
    
    poi.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(poi)
    return poi

@router.delete("/pois/{poi_id}")
async def delete_poi(poi_id: int, db: Session = Depends(get_db)):
    """Delete a Point of Interest"""
    poi = db.query(PointOfInterest).filter(PointOfInterest.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    
    poi.is_active = False
    db.commit()
    return {"message": "POI deleted successfully"}

# Routing Graph Management
@router.post("/versions/{version_id}/routing/nodes", response_model=RoutingNode)
async def create_routing_node(node: RoutingNodeCreate, db: Session = Depends(get_db)):
    """Create a routing node"""
    version = db.query(FloorPlanVersion).filter(FloorPlanVersion.id == node.version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    db_node = RoutingNode(**node.dict())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

@router.get("/versions/{version_id}/routing/nodes", response_model=List[RoutingNode])
async def get_routing_nodes(version_id: int, db: Session = Depends(get_db)):
    """Get all routing nodes for a version"""
    nodes = db.query(RoutingNode).filter(
        RoutingNode.version_id == version_id,
        RoutingNode.is_active == True
    ).all()
    return nodes

@router.post("/versions/{version_id}/routing/edges", response_model=RoutingEdge)
async def create_routing_edge(edge: RoutingEdgeCreate, db: Session = Depends(get_db)):
    """Create a routing edge"""
    version = db.query(FloorPlanVersion).filter(FloorPlanVersion.id == edge.version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Validate nodes exist
    from_node = db.query(RoutingNode).filter(RoutingNode.id == edge.from_node_id).first()
    to_node = db.query(RoutingNode).filter(RoutingNode.id == edge.to_node_id).first()
    
    if not from_node or not to_node:
        raise HTTPException(status_code=404, detail="One or both nodes not found")
    
    db_edge = RoutingEdge(**edge.dict())
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge

@router.get("/versions/{version_id}/routing/edges", response_model=List[RoutingEdge])
async def get_routing_edges(version_id: int, db: Session = Depends(get_db)):
    """Get all routing edges for a version"""
    edges = db.query(RoutingEdge).filter(
        RoutingEdge.version_id == version_id,
        RoutingEdge.is_active == True
    ).all()
    return edges

# Map Validation and Publishing
@router.post("/versions/{version_id}/validate", response_model=MapValidationResult)
async def validate_map(version_id: int, db: Session = Depends(get_db)):
    """Validate a map version"""
    version = db.query(FloorPlanVersion).filter(FloorPlanVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    errors = []
    warnings = []
    
    # Check POIs
    pois = db.query(PointOfInterest).filter(
        PointOfInterest.version_id == version_id,
        PointOfInterest.is_active == True
    ).all()
    
    if len(pois) == 0:
        warnings.append("No Points of Interest defined")
    
    # Check routing graph
    nodes = db.query(RoutingNode).filter(
        RoutingNode.version_id == version_id,
        RoutingNode.is_active == True
    ).all()
    
    edges = db.query(RoutingEdge).filter(
        RoutingEdge.version_id == version_id,
        RoutingEdge.is_active == True
    ).all()
    
    if len(nodes) == 0:
        errors.append("No routing nodes defined")
    
    if len(nodes) > 0 and len(edges) == 0:
        warnings.append("Routing nodes exist but no edges defined")
    
    # Check graph connectivity
    if len(nodes) > 0:
        # Simple connectivity check - ensure all nodes are connected
        connected_nodes = set()
        if nodes:
            connected_nodes.add(nodes[0].id)
            
            # Find all connected nodes
            changed = True
            while changed:
                changed = False
                for edge in edges:
                    if edge.from_node_id in connected_nodes and edge.to_node_id not in connected_nodes:
                        connected_nodes.add(edge.to_node_id)
                        changed = True
                    elif edge.to_node_id in connected_nodes and edge.from_node_id not in connected_nodes:
                        connected_nodes.add(edge.from_node_id)
                        changed = True
        
        disconnected_nodes = [node.id for node in nodes if node.id not in connected_nodes]
        if disconnected_nodes:
            warnings.append(f"Nodes {disconnected_nodes} are not connected to the main graph")
    
    statistics = {
        "pois_count": len(pois),
        "nodes_count": len(nodes),
        "edges_count": len(edges),
        "connected_nodes": len(connected_nodes) if nodes else 0
    }
    
    is_valid = len(errors) == 0
    
    return MapValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        statistics=statistics
    )

@router.post("/versions/{version_id}/publish", response_model=MapPublishingWorkflow)
async def publish_map_version(
    version_id: int,
    published_by: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Publish a map version"""
    version = db.query(FloorPlanVersion).filter(FloorPlanVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Validate first
    validation_result = await validate_map(version_id, db)
    
    # Create publishing record
    publishing = MapPublishing(
        floor_id=version.floor_id,
        version_id=version_id,
        status="review" if validation_result.is_valid else "draft",
        published_by=published_by,
        validation_results=validation_result.dict()
    )
    
    db.add(publishing)
    db.commit()
    db.refresh(publishing)
    
    # Determine next steps
    next_steps = []
    if not validation_result.is_valid:
        next_steps.extend(["Fix validation errors", "Re-validate map"])
    else:
        next_steps.extend(["Review map", "Approve for publishing"])
    
    return MapPublishingWorkflow(
        version_id=version_id,
        validation_result=validation_result,
        publishing_status=publishing.status,
        next_steps=next_steps
    )

@router.get("/floors/{floor_id}/publishing", response_model=List[MapPublishing])
async def get_publishing_history(floor_id: int, db: Session = Depends(get_db)):
    """Get publishing history for a floor"""
    publishing = db.query(MapPublishing).filter(
        MapPublishing.floor_id == floor_id
    ).order_by(MapPublishing.created_at.desc()).all()
    return publishing
