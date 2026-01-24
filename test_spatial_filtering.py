"""
Test script for spatial filtering functionality.

This script tests the three spatial filtering modes:
1. Polygon containment
2. Nearest X buildings
3. Radius filtering
"""

from backend.scripts.nodes.spatial_filtering import (
    spatial_filtering,
    parse_building_geometry,
    extract_buildings_list,
    filter_by_polygon,
    filter_by_nearest,
    filter_by_radius
)
from shapely import wkt
from shapely.geometry import Point

# Test data: Mock buildings with WKT geometries in EPSG:25833
test_buildings = [
    {
        "id": "BUILDING_001",
        "name": "Building 1",
        "geometry_geojson": "POINT(388000 5819000)"  # Center
    },
    {
        "id": "BUILDING_002",
        "name": "Building 2",
        "geometry_geojson": "POINT(388100 5819000)"  # 100m east
    },
    {
        "id": "BUILDING_003",
        "name": "Building 3",
        "geometry_geojson": "POINT(388000 5819100)"  # 100m north
    },
    {
        "id": "BUILDING_004",
        "name": "Building 4",
        "geometry_geojson": "POINT(388500 5819000)"  # 500m east
    },
    {
        "id": "BUILDING_005",
        "name": "Building 5",
        "geometry_geojson": "POINT(387800 5818800)"  # ~280m southwest
    }
]


def test_parse_geometry():
    """Test WKT geometry parsing."""
    print("\n=== Test: Parse Building Geometry ===")
    
    for building in test_buildings[:2]:
        try:
            point = parse_building_geometry(building)
            print(f"{building['id']}: {point}")
        except ValueError as e:
            print(f"ERROR: {e}")
    
    print("✓ Geometry parsing test complete")


def test_polygon_filtering():
    """Test polygon containment filtering."""
    print("\n=== Test: Polygon Filtering ===")
    
    # Create a polygon that contains only buildings 1, 2, 3
    polygon_wkt = "POLYGON((387900 5818900, 388200 5818900, 388200 5819200, 387900 5819200, 387900 5818900))"
    polygon = wkt.loads(polygon_wkt)
    
    filtered = filter_by_polygon(test_buildings, polygon)
    print(f"Original buildings: {len(test_buildings)}")
    print(f"Filtered buildings: {len(filtered)}")
    print(f"Building IDs: {[b['id'] for b in filtered]}")
    
    assert len(filtered) == 3, f"Expected 3 buildings, got {len(filtered)}"
    print("✓ Polygon filtering test passed")


def test_nearest_filtering():
    """Test nearest X buildings filtering."""
    print("\n=== Test: Nearest Buildings ===")
    
    # Find nearest 3 buildings to center point
    center_point = Point(388000, 5819000)
    
    filtered = filter_by_nearest(test_buildings, center_point, count=3)
    print(f"Nearest 3 buildings to center:")
    for building in filtered:
        distance = building.get("_distance", 0)
        print(f"  {building['id']}: {distance:.1f}m")
    
    assert len(filtered) == 3, f"Expected 3 buildings, got {len(filtered)}"
    assert filtered[0]['id'] == "BUILDING_001", "First should be BUILDING_001 (center)"
    print("✓ Nearest buildings test passed")


def test_radius_filtering():
    """Test radius-based filtering."""
    print("\n=== Test: Radius Filtering ===")
    
    # Find buildings within 300m of center
    center_point = Point(388000, 5819000)
    
    filtered = filter_by_radius(test_buildings, center_point, radius=300)
    print(f"Buildings within 300m:")
    for building in filtered:
        distance = building.get("_distance", 0)
        print(f"  {building['id']}: {distance:.1f}m")
    
    # Should include buildings 1, 2, 3, 5 (all within 300m)
    assert len(filtered) == 4, f"Expected 4 buildings, got {len(filtered)}"
    print("✓ Radius filtering test passed")


def test_full_node():
    """Test the complete spatial_filtering node."""
    print("\n=== Test: Full Spatial Filtering Node ===")
    
    # Test with polygon
    state_polygon = {
        "query": "Zeige mir alle Gebäude in diesem Bereich",
        "spatial_filter": "POLYGON((387900 5818900, 388200 5818900, 388200 5819200, 387900 5819200, 387900 5818900))",
        "results": test_buildings,
        "messages": []
    }
    
    result = spatial_filtering(state_polygon)
    print(f"Polygon mode: {len(extract_buildings_list(result['results']))} buildings filtered")
    print(f"Spatial comparison: {result.get('spatial_comparison', {})}")
    
    # Test with point (nearest)
    state_nearest = {
        "query": "Zeige mir die 3 nächsten Gebäude",
        "spatial_filter": "POINT(388000 5819000)",
        "results": test_buildings,
        "messages": []
    }
    
    result = spatial_filtering(state_nearest)
    print(f"\nPoint mode (should detect 'nearest'): {len(extract_buildings_list(result['results']))} buildings")
    print(f"Spatial comparison: {result.get('spatial_comparison', {})}")
    
    # Test with point (radius)
    state_radius = {
        "query": "Finde alle Gebäude im Umkreis von 300m",
        "spatial_filter": "POINT(388000 5819000)",
        "results": test_buildings,
        "messages": []
    }
    
    result = spatial_filtering(state_radius)
    print(f"\nPoint mode (should detect 'radius'): {len(extract_buildings_list(result['results']))} buildings")
    print(f"Spatial comparison: {result.get('spatial_comparison', {})}")
    
    print("✓ Full node test complete")


if __name__ == "__main__":
    print("=" * 60)
    print("SPATIAL FILTERING TESTS")
    print("=" * 60)
    
    try:
        test_parse_geometry()
        test_polygon_filtering()
        test_nearest_filtering()
        test_radius_filtering()
        test_full_node()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
