"""
Statistics Calculation Node

Calculates descriptive statistics from building results before answer generation.
Computes min, mean, max for area and floors_above, and min/max for house_number.
"""

from typing import Dict, Any, List
import re
from ..models import AgentState


def extract_numeric_from_house_number(house_number: str) -> int | None:
    """
    Extract numeric part from house number string.
    
    Examples:
        "12" -> 12
        "12a" -> 12
        "4c" -> 4
        "abc" -> None
    
    Args:
        house_number: House number string
        
    Returns:
        Numeric part as integer, or None if no number found
    """
    if not house_number:
        return None
    
    match = re.search(r'\d+', house_number)
    if match:
        return int(match.group())
    return None


def calculate_building_statistics(buildings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate descriptive statistics for building attributes.
    
    Statistics:
        - area: min, mean, max (parsed from string with "." decimal separator)
        - floors_above: min, mean, max (integer)
        - house_number: min, max (numeric part only)
    
    Args:
        buildings: List of building dictionaries
        
    Returns:
        Dictionary with calculated statistics
    """
    if not buildings:
        return {}
    
    # Collect valid values
    areas = []
    floors = []
    house_numbers = []
    
    for building in buildings:
        # Parse area (string with "." as decimal separator)
        area_str = building.get("area")
        if area_str:
            try:
                areas.append(float(area_str))
            except (ValueError, TypeError):
                pass
        
        # Parse floors_above (should be integer)
        floors_above = building.get("floors_above")
        if floors_above is not None:
            try:
                floors.append(int(floors_above))
            except (ValueError, TypeError):
                pass
        
        # Parse house_number (extract numeric part)
        house_number = building.get("house_number")
        if house_number:
            numeric_part = extract_numeric_from_house_number(str(house_number))
            if numeric_part is not None:
                house_numbers.append(numeric_part)
    
    # Calculate statistics
    stats = {}
    
    # Area statistics
    if areas:
        stats["area_min"] = round(min(areas), 2)
        stats["area_max"] = round(max(areas), 2)
        stats["area_mean"] = round(sum(areas) / len(areas), 2)
    
    # Floors statistics
    if floors:
        stats["floors_above_min"] = min(floors)
        stats["floors_above_max"] = max(floors)
        stats["floors_above_mean"] = round(sum(floors) / len(floors), 2)
    
    # House number statistics
    if house_numbers:
        stats["house_number_min"] = min(house_numbers)
        stats["house_number_max"] = max(house_numbers)
    
    # Building count
    stats["building_count"] = len(buildings)
    
    return stats


def statistics_calculation(state: AgentState) -> Dict[str, Any]:
    """
    Calculate statistics from query results and add to results structure.
    
    Transforms results from:
        [{"buildings": [...]}]
    
    To:
        [{"buildings": [...], "statistics": {...}}]
    
    Args:
        state: Current agent state with results
        
    Returns:
        Updated state with statistics added to results
    """
    results = state.get("results", [])
    
    # Handle empty results
    if not results:
        return {
            "messages": ["No results to calculate statistics from"]
        }
    
    # Extract buildings from results structure
    buildings = []
    if isinstance(results, list) and len(results) > 0:
        if isinstance(results[0], dict) and "buildings" in results[0]:
            # Already in structured format: [{"buildings": [...]}]
            buildings = results[0].get("buildings", [])
        else:
            # Direct list of buildings: [building1, building2, ...]
            buildings = results
    
    # Calculate statistics
    statistics = calculate_building_statistics(buildings)
    
    # Update results structure
    updated_results = [
        {
            "buildings": buildings,
            "statistics": statistics
        }
    ]
    
    return {
        "results": updated_results,
        "messages": [f"Calculated statistics for {statistics.get('building_count', 0)} buildings"]
    }
