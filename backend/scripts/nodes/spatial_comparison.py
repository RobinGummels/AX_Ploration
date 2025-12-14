"""Node for spatial comparison and processing of results."""

from typing import Dict, Any, List, Optional

from ..models import AgentState


def spatial_comparison(state: AgentState) -> Dict[str, Any]:
    """
    Node: Perform spatial comparison on query results.
    
    For nearby and custom_area queries, this node can:
    - Calculate distances between points
    - Filter results by spatial criteria
    - Add spatial metadata to results
    
    Args:
        state: Current agent state with 'results' from Neo4j
        
    Returns:
        Dict with 'spatial_comparison' analysis
    """
    results = state.get("results", [])
    query_type = state.get("query_type", "")
    
    if not results:
        return {
            "spatial_comparison": None,
            "messages": ["No results to perform spatial comparison on"]
        }
    
    try:
        spatial_analysis = {
            "total_results": len(results),
            "query_type": query_type,
            "has_geometry": False,
            "statistics": {}
        }
        
        # Check if results contain geometry data
        if results and any("geometry" in r or "location" in r for r in results):
            spatial_analysis["has_geometry"] = True
            
            # Calculate basic statistics if applicable
            if query_type == "nearby":
                # For nearby queries, we might have distance information
                distances = [r.get("distance") for r in results if r.get("distance") is not None]
                if distances:
                    spatial_analysis["statistics"] = {
                        "min_distance": min(distances),
                        "max_distance": max(distances),
                        "avg_distance": sum(distances) / len(distances)
                    }
        
        # Calculate other statistics from numeric fields
        numeric_fields = ["height", "area", "floors_above", "floors_below"]
        for field in numeric_fields:
            values = [r.get(field) for r in results if r.get(field) is not None]
            if values:
                spatial_analysis["statistics"][field] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
        
        return {
            "spatial_comparison": spatial_analysis,
            "messages": [f"Spatial analysis completed: {len(results)} results analyzed"]
        }
        
    except Exception as e:
        return {
            "spatial_comparison": None,
            "error": f"Error in spatial comparison: {str(e)}",
            "messages": [f"Error in spatial comparison: {str(e)}"]
        }
