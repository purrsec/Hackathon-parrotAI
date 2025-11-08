"""
Example: Converting Sphinx local coordinates to GPS coordinates.
"""

from .coordinate_converter import convert_sphinx_coordinates, CoordinateConverter
from . import load_world_map


def example_convert_sphinx_coords():
    """Convert Sphinx local coordinates to GPS."""
    # Sphinx gives you local coordinates
    local_x = 100.0
    local_y = 110.0
    local_z = 20.0  # altitude in meters
    
    # Convert to GPS
    lat, lon, alt = convert_sphinx_coordinates(local_x, local_y, local_z)
    
    print(f"Sphinx local: ({local_x}, {local_y}, {local_z})")
    print(f"GPS: ({lat:.12f}, {lon:.12f}, {alt:.1f})")
    
    return lat, lon, alt


def example_convert_poi_to_gps():
    """Convert a POI from Sphinx local coordinates to GPS for world map."""
    # You have a POI at Sphinx local coordinates
    poi_local_x = 50.0
    poi_local_y = 75.0
    poi_height = 25.0  # building height
    
    # Convert to GPS
    lat, lon, _ = convert_sphinx_coordinates(poi_local_x, poi_local_y, 0)
    
    # Create POI entry for world map
    poi = {
        "name": "Factory Building",
        "type": "factory",
        "coordinates": {
            "latitude": lat,
            "longitude": lon,
            "altitude_meters": 0.0
        },
        "height_meters": poi_height,
        "description": "Main factory building"
    }
    
    print("POI for world map:")
    print(f"  Local: ({poi_local_x}, {poi_local_y})")
    print(f"  GPS: ({lat:.12f}, {lon:.12f})")
    print(f"  Height: {poi_height}m")
    
    return poi


if __name__ == "__main__":
    print("=" * 80)
    print("Example 1: Convert Sphinx Coordinates")
    print("=" * 80)
    example_convert_sphinx_coords()
    
    print("\n" + "=" * 80)
    print("Example 2: Convert POI to GPS")
    print("=" * 80)
    example_convert_poi_to_gps()

