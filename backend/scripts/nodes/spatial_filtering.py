"""
Spatial Filtering Node

Performs local spatial analysis on building results based on user-provided WKT geometry.
Operates after Cypher query execution using shapely for geometry operations.

Three filtering modes:
1. Polygon/MultiPolygon: Filter buildings by containment
2. Point + "nearest X": Sort by distance, return top X buildings
3. Point + "radius X": Filter buildings within distance threshold
"""

from typing import Dict, Any, List
import json
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection, shape
from shapely.errors import ShapelyError

from ..models import AgentState
from ..utils.llm_client import llm_client


def parse_building_geometry(building: Dict[str, Any]) -> Point:
    """
    Parse building geometry from WKT string or GeoJSON.
    
    Args:
        building: Building dict with geometry_geojson or centroid field
        
    Returns:
        Shapely Point representing building centroid
        
    Raises:
        ValueError: If geometry cannot be parsed
    """
    # Try centroid first (faster, already a point)
    centroid_wkt = building.get("centroid")
    if centroid_wkt:
        try:
            # Fix format: "Point (x y)" -> "POINT(x y)"
            if centroid_wkt.startswith("Point "):
                centroid_wkt = "POINT" + centroid_wkt[5:]  # Replace "Point " with "POINT"
            
            geom = wkt.loads(centroid_wkt)
            if isinstance(geom, Point):
                return geom
        except ShapelyError:
            pass  # Fall through to try geometry_geojson
    
    # Try geometry_geojson
    geometry_data = building.get("geometry_geojson")
    if not geometry_data:
        raise ValueError(f"Building {building.get('id', 'unknown')} has no geometry")
    
    try:
        # Check if it's a JSON string (GeoJSON format)
        if isinstance(geometry_data, str) and geometry_data.strip().startswith("{"):
            geojson = json.loads(geometry_data)
            # Use shapely's shape to convert GeoJSON to geometry
            geom = shape(geojson)
        else:
            # Assume it's WKT
            geom = wkt.loads(geometry_data)
        
        # If it's a polygon/multipolygon, use centroid
        if isinstance(geom, (Polygon, MultiPolygon, GeometryCollection)):
            return geom.centroid
        elif isinstance(geom, Point):
            return geom
        else:
            raise ValueError(f"Unsupported geometry type: {type(geom)}")
            
    except (ShapelyError, json.JSONDecodeError, Exception) as e:
        raise ValueError(f"Failed to parse geometry: {str(e)}")


def extract_buildings_list(results: Any) -> List[Dict[str, Any]]:
    """
    Extract buildings list from results, handling both array and object structures.
    
    Args:
        results: Either a list of buildings or an object with 'buildings' field
        
    Returns:
        List of building dictionaries
    """
    if isinstance(results, list):
        # Check if it's a list with a single dict containing 'buildings'
        if len(results) > 0 and isinstance(results[0], dict) and "buildings" in results[0]:
            # Nested structure: [{"buildings": [...]}]
            return results[0]["buildings"]
        else:
            # Direct array of buildings
            return results
    elif isinstance(results, dict) and "buildings" in results:
        # Object with buildings field
        return results["buildings"]
    else:
        # No buildings found or unexpected structure
        return []


def update_results_structure(state: AgentState, filtered_buildings: List[Dict[str, Any]]) -> Any:
    """
    Update results maintaining the original structure (array vs object).
    
    Args:
        state: Current agent state
        filtered_buildings: Filtered list of buildings
        
    Returns:
        Results in the same structure as original
    """
    original_results = state.get("results", [])
    
    if isinstance(original_results, list):
        # Return as array
        return filtered_buildings
    elif isinstance(original_results, dict) and "buildings" in original_results:
        # Return as object with updated buildings
        updated_results = original_results.copy()
        updated_results["buildings"] = filtered_buildings
        return updated_results
    else:
        # Fallback to array
        return filtered_buildings


def determine_point_filter_mode(query: str, spatial_filter_wkt: str) -> Dict[str, Any]:
    """
    Use LLM to determine if query wants 'nearest X' or 'radius X' filtering.
    
    Args:
        query: User's original query
        spatial_filter_wkt: WKT Point geometry
        
    Returns:
        Dict with 'mode' ('nearest' or 'radius') and 'value' (number)
    """
    prompt = f"""Analysiere die folgende Benutzeranfrage und bestimme, welche Art von räumlicher Filterung gewünscht ist.

Benutzeranfrage: "{query}"
Räumlicher Filter: Punkt-Geometrie (WKT: {spatial_filter_wkt})

Der Benutzer möchte entweder:
1. Die **nächstgelegenen X Gebäude** zu diesem Punkt finden
2. Alle Gebäude **innerhalb eines Radius X** um diesen Punkt finden

Antworte im JSON-Format:
{{
    "mode": "nearest" oder "radius",
    "value": <Zahl>,
    "reasoning": "Kurze Erklärung"
}}

Beispiele:
- "Zeige mir die 5 nächsten Schulen" → {{"mode": "nearest", "value": 5}}
- "Finde alle Gebäude im Umkreis von 500m" → {{"mode": "radius", "value": 500}}
- "Welche Krankenhäuser sind in der Nähe?" → {{"mode": "nearest", "value": 10}} (Standard: 10)
- "Gebäude innerhalb von 1km" → {{"mode": "radius", "value": 1000}}

Wenn keine spezifische Zahl genannt wird:
- Für "nächste/nearest": Verwende value=10 als Standard
- Für "Umkreis/radius": Verwende value=500 als Standard (in Metern)

Antworte NUR mit dem JSON-Objekt, keine zusätzlichen Erklärungen."""

    try:
        response = llm_client.chat_completion_json([{"role": "user", "content": prompt}], temperature=0)
        
        mode = response.get("mode", "nearest")
        value = response.get("value", 10 if mode == "nearest" else 500)
        reasoning = response.get("reasoning", "")
        
        return {
            "mode": mode,
            "value": value,
            "reasoning": reasoning
        }
        
    except Exception as e:
        # Fallback to nearest 10 if LLM fails
        return {
            "mode": "nearest",
            "value": 10,
            "reasoning": f"Fallback due to error: {str(e)}"
        }


def filter_by_polygon(
    buildings: List[Dict[str, Any]], 
    polygon: Polygon | MultiPolygon
) -> List[Dict[str, Any]]:
    """
    Filter buildings by polygon containment.
    
    Args:
        buildings: List of building dictionaries
        polygon: Shapely Polygon or MultiPolygon
        
    Returns:
        List of buildings whose centroids are within the polygon
    """
    filtered = []
    
    for building in buildings:
        try:
            building_point = parse_building_geometry(building)
            if polygon.contains(building_point):
                filtered.append(building)
        except ValueError:
            # Skip buildings with invalid geometry
            continue
    
    return filtered


def filter_by_nearest(
    buildings: List[Dict[str, Any]], 
    point: Point, 
    count: int
) -> List[Dict[str, Any]]:
    """
    Filter buildings by distance, returning nearest X buildings.
    
    Args:
        buildings: List of building dictionaries
        point: Reference point
        count: Number of nearest buildings to return
        
    Returns:
        List of nearest buildings, sorted by distance
    """
    buildings_with_distance = []
    
    for building in buildings:
        try:
            building_point = parse_building_geometry(building)
            distance = point.distance(building_point)
            
            # Add distance to building data
            building_copy = building.copy()
            building_copy["_distance"] = distance
            buildings_with_distance.append(building_copy)
            
        except ValueError:
            # Skip buildings with invalid geometry
            continue
    
    # Sort by distance and take top N
    buildings_with_distance.sort(key=lambda b: b["_distance"])
    return buildings_with_distance[:count]


def filter_by_radius(
    buildings: List[Dict[str, Any]], 
    point: Point, 
    radius: float
) -> List[Dict[str, Any]]:
    """
    Filter buildings within radius (in meters) from point.
    
    Args:
        buildings: List of building dictionaries
        point: Reference point
        radius: Maximum distance in meters
        
    Returns:
        List of buildings within radius, sorted by distance
    """
    buildings_with_distance = []
    
    for building in buildings:
        try:
            building_point = parse_building_geometry(building)
            distance = point.distance(building_point)
            
            if distance <= radius:
                # Add distance to building data
                building_copy = building.copy()
                building_copy["_distance"] = distance
                buildings_with_distance.append(building_copy)
                
        except ValueError:
            # Skip buildings with invalid geometry
            continue
    
    # Sort by distance
    buildings_with_distance.sort(key=lambda b: b["_distance"])
    return buildings_with_distance


def spatial_filtering(state: AgentState) -> Dict[str, Any]:
    """
    Perform spatial filtering on query results based on user-provided geometry.
    
    Modes:
    1. Polygon/MultiPolygon → Filter by containment
    2. Point → Ask LLM if "nearest X" or "radius X", then filter accordingly
    
    Args:
        state: Current agent state with results and spatial_filter
        
    Returns:
        Updated state with filtered results and spatial_comparison metadata
    """
    spatial_filter_wkt = state.get("spatial_filter")
    
    # Skip if no spatial filter provided
    if not spatial_filter_wkt:
        return {
            "messages": ["No spatial filter provided, skipping spatial filtering"]
        }
    
    # Parse spatial filter geometry
    try:
        filter_geometry = wkt.loads(spatial_filter_wkt)
    except ShapelyError as e:
        return {
            "error": f"Invalid WKT geometry: {str(e)}",
            "messages": [f"Failed to parse spatial filter WKT: {str(e)}"]
        }
    
    # Extract buildings from results
    buildings = extract_buildings_list(state.get("results", []))
    original_count = len(buildings)
    
    if original_count == 0:
        return {
            "messages": ["No buildings in results to filter"]
        }
    
    # Determine filtering mode based on geometry type
    geometry_type = filter_geometry.geom_type
    filtered_buildings = []
    filter_info = {}
    
    try:
        if geometry_type in ["Polygon", "MultiPolygon"]:
            # Mode 1: Filter by polygon containment
            filtered_buildings = filter_by_polygon(buildings, filter_geometry)
            filter_info = {
                "mode": "polygon_containment",
                "geometry_type": geometry_type,
                "original_count": original_count,
                "filtered_count": len(filtered_buildings)
            }
            message = f"Filtered buildings by polygon containment: {original_count} → {len(filtered_buildings)} buildings"
            
        elif geometry_type == "Point":
            # Mode 2 or 3: Determine from query using LLM
            point_filter = determine_point_filter_mode(state.get("query", ""), spatial_filter_wkt)
            mode = point_filter["mode"]
            value = point_filter["value"]
            
            if mode == "nearest":
                # Mode 2: Nearest X buildings
                filtered_buildings = filter_by_nearest(buildings, filter_geometry, value)
                filter_info = {
                    "mode": "nearest",
                    "count": value,
                    "original_count": original_count,
                    "filtered_count": len(filtered_buildings),
                    "reasoning": point_filter.get("reasoning", "")
                }
                message = f"Filtered nearest {value} buildings: {original_count} → {len(filtered_buildings)} buildings"
                
            else:  # mode == "radius"
                # Mode 3: Buildings within radius
                filtered_buildings = filter_by_radius(buildings, filter_geometry, value)
                filter_info = {
                    "mode": "radius",
                    "radius_meters": value,
                    "original_count": original_count,
                    "filtered_count": len(filtered_buildings),
                    "reasoning": point_filter.get("reasoning", "")
                }
                message = f"Filtered buildings within {value}m radius: {original_count} → {len(filtered_buildings)} buildings"
        
        else:
            return {
                "error": f"Unsupported geometry type: {geometry_type}",
                "messages": [f"Cannot filter by geometry type {geometry_type}"]
            }
        
        # Update results maintaining original structure
        updated_results = update_results_structure(state, filtered_buildings)
        
        return {
            "results": updated_results,
            "pre_filter_results": state.get("results"),  # Save original results before filtering
            "spatial_comparison": filter_info,
            "messages": [message]
        }
        
    except Exception as e:
        return {
            "error": f"Spatial filtering failed: {str(e)}",
            "messages": [f"Error during spatial filtering: {str(e)}"]
        }
