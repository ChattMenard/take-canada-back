"""Visualization data router for evidence dashboard."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import Dict, List, Any

router = APIRouter(prefix="/api/visualization", tags=["visualization"])

# Path to extracted visualization data
DATA_DIR = Path(__file__).parent.parent / "data"

@router.get("/timeline")
async def get_timeline_events() -> Dict[str, Any]:
    """Get timeline events for visualization."""
    try:
        with open(DATA_DIR / "timeline_events.json", "r") as f:
            data = json.load(f)
        return {"events": data, "count": len(data)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Timeline data not found")

@router.get("/network")
async def get_network_data() -> Dict[str, Any]:
    """Get network graph data (nodes and edges)."""
    try:
        with open(DATA_DIR / "network_nodes.json", "r") as f:
            nodes = json.load(f)
        
        # Generate edges from timeline events and financial flows
        with open(DATA_DIR / "financial_flows.json", "r") as f:
            flows = json.load(f)
        
        edges = []
        for flow in flows:
            edges.append({
                "source": flow["source"].lower().replace(" ", "_"),
                "target": flow["target"].lower().replace(" ", "_"),
                "type": "funding",
                "amount": flow["amount"],
                "category": flow["category"]
            })
        
        return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Network data not found")

@router.get("/financial-flow")
async def get_financial_flows() -> Dict[str, Any]:
    """Get financial flow data for Sankey diagram."""
    try:
        with open(DATA_DIR / "financial_flows.json", "r") as f:
            data = json.load(f)
        return {"flows": data, "count": len(data)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Financial flow data not found")

@router.get("/lobbying")
async def get_lobbying_meetings() -> Dict[str, Any]:
    """Get lobbying meeting data for heatmap."""
    try:
        with open(DATA_DIR / "lobbying_meetings.json", "r") as f:
            data = json.load(f)
        return {"meetings": data, "count": len(data)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Lobbying data not found")

@router.get("/all")
async def get_all_visualization_data() -> Dict[str, Any]:
    """Get all visualization data in single response."""
    try:
        with open(DATA_DIR / "visualization_data.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Visualization data not found")

@router.get("/vaccine-waste")
async def get_vaccine_waste_data() -> Dict[str, Any]:
    """Get vaccine waste data for bar chart."""
    # Static data from evidence files
    return {
        "purchased": 169000000,
        "administered": 85000000,
        "wasted": 40000000,
        "expired": 13600000,
        "donated": 15300000,
        "waste_cost_billion": 1.2,
        "per_dose_cost": 25,
        "source": "Auditor General Report 6 (Nov 2022), Report 1 (May 2023)"
    }

@router.get("/revolving-door")
async def get_revolving_door_data() -> Dict[str, Any]:
    """Get revolving door personnel data."""
    # Static data from ethics disclosures investigation
    return {
        "individuals": [
            {
                "name": "Pamela Fralick",
                "from": "Innovative Medicines Canada",
                "to": "Government Advisor",
                "date": "2021",
                "conflict_score": 85
            }
        ],
        "source": "ETHICS_DISCLOSURES_INVESTIGATION.md"
    }
