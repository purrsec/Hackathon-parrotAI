"""
Utility to add Sphinx local coordinates to industrial city map as GPS coordinates.
"""

import json
from pathlib import Path
from typing import Optional
from .coordinate_converter import convert_sphinx_coordinates


def add_poi_to_map(
    map_file: str,
    name: str,
    local_x: float,
    local_y: float,
    altitude_meters: float = 0.0,
    poi_type: str = "landmark",
    description: Optional[str] = None
):
    """
    Add a Point of Interest to the world map from Sphinx local coordinates.
    
    Args:
        map_file: Path to the world map JSON file
        name: Name of the POI
        local_x: Sphinx local x coordinate
        local_y: Sphinx local y coordinate
        altitude_meters: Altitude of the POI (where to point the camera)
        poi_type: Type of POI (landmark, factory, warehouse, etc.)
        description: Optional description
    """
    # Load map
    with open(map_file, "r", encoding="utf-8") as f:
        world_map = json.load(f)
    
    # Convert local coordinates to GPS
    lat, lon, _ = convert_sphinx_coordinates(local_x, local_y, 0)
    
    # Create POI entry
    poi = {
        "name": name,
        "type": poi_type,
        "coordinates": {
            "latitude": lat,
            "longitude": lon,
            "altitude_meters": altitude_meters
        }
    }
    
    if description:
        poi["description"] = description
    
    # Add to map
    if "points_of_interest" not in world_map:
        world_map["points_of_interest"] = []
    
    world_map["points_of_interest"].append(poi)
    
    # Save map
    with open(map_file, "w", encoding="utf-8") as f:
        json.dump(world_map, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Added POI '{name}' at local ({local_x}, {local_y}) -> GPS ({lat:.12f}, {lon:.12f}), altitude: {altitude_meters}m")
    return poi


def add_obstacle_to_map(
    map_file: str,
    name: str,
    local_x: float,
    local_y: float,
    height_meters: float,
    obstacle_type: str = "building",
    description: Optional[str] = None
):
    """
    Add an obstacle to the world map from Sphinx local coordinates.
    
    Args:
        map_file: Path to the world map JSON file
        name: Name of the obstacle
        local_x: Sphinx local x coordinate
        local_y: Sphinx local y coordinate
        height_meters: Height of the obstacle in meters
        obstacle_type: Type of obstacle (building, tower, structure, etc.)
        description: Optional description
    """
    # Load map
    with open(map_file, "r", encoding="utf-8") as f:
        world_map = json.load(f)
    
    # Convert local coordinates to GPS
    lat, lon, _ = convert_sphinx_coordinates(local_x, local_y, 0)
    
    # Create obstacle entry
    obstacle = {
        "name": name,
        "type": obstacle_type,
        "coordinates": {
            "latitude": lat,
            "longitude": lon,
            "altitude_meters": 0.0
        },
        "height_meters": height_meters
    }
    
    if description:
        obstacle["description"] = description
    
    # Add to map
    if "obstacles" not in world_map:
        world_map["obstacles"] = []
    
    world_map["obstacles"].append(obstacle)
    
    # Save map
    with open(map_file, "w", encoding="utf-8") as f:
        json.dump(world_map, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Added obstacle '{name}' at local ({local_x}, {local_y}) -> GPS ({lat:.12f}, {lon:.12f}), height: {height_meters}m")
    return obstacle


def add_boundary_to_map(
    map_file: str,
    name: str,
    local_coordinates: list,
    boundary_type: str = "polygon",
    geofence_type: str = "geofence",
    max_altitude_meters: Optional[float] = None,
    description: Optional[str] = None
):
    """
    Add a boundary to the world map from Sphinx local coordinates.
    
    Args:
        map_file: Path to the world map JSON file
        name: Name of the boundary
        local_coordinates: List of (x, y) tuples in local coordinates
        boundary_type: "polygon" or "circle"
        geofence_type: "geofence", "no_fly_zone", or "restricted"
        max_altitude_meters: Maximum altitude in meters (optional)
        description: Optional description
    """
    # Load map
    with open(map_file, "r", encoding="utf-8") as f:
        world_map = json.load(f)
    
    # Convert local coordinates to GPS
    gps_coords = []
    for coord in local_coordinates:
        if len(coord) == 2:
            local_x, local_y = coord
            lat, lon, _ = convert_sphinx_coordinates(local_x, local_y, 0)
            gps_coords.append([lat, lon])
        else:
            raise ValueError("Each coordinate must be (x, y) tuple")
    
    # Create boundary entry
    boundary = {
        "name": name,
        "type": geofence_type,
        "boundary_type": boundary_type,
        "coordinates": gps_coords
    }
    
    if max_altitude_meters is not None:
        boundary["max_altitude_meters"] = max_altitude_meters
    
    if description:
        boundary["description"] = description
    
    # Add to map
    if "boundaries" not in world_map:
        world_map["boundaries"] = []
    
    world_map["boundaries"].append(boundary)
    
    # Save map
    with open(map_file, "w", encoding="utf-8") as f:
        json.dump(world_map, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Added boundary '{name}' with {len(gps_coords)} points")
    return boundary


# Convenience function for quick additions
def add_to_industrial_city(
    item_type: str,
    name: str,
    local_x: float,
    local_y: float,
    **kwargs
):
    """
    Quick function to add items to industrial_city.json.
    
    Args:
        item_type: "poi", "obstacle", or "boundary"
        name: Name of the item
        local_x: Sphinx local x coordinate
        local_y: Sphinx local y coordinate
        **kwargs: Additional arguments (altitude_meters, type, description, etc.)
    """
    map_file = "maps/industrial_city.json"
    
    if item_type == "poi":
        return add_poi_to_map(
            map_file, name, local_x, local_y,
            altitude_meters=kwargs.get("altitude_meters", 0.0),
            poi_type=kwargs.get("type", "landmark"),
            description=kwargs.get("description")
        )
    elif item_type == "obstacle":
        if "height_meters" not in kwargs:
            raise ValueError("height_meters is required for obstacles")
        return add_obstacle_to_map(
            map_file, name, local_x, local_y,
            height_meters=kwargs["height_meters"],
            obstacle_type=kwargs.get("type", "building"),
            description=kwargs.get("description")
        )
    else:
        raise ValueError(f"Unknown item_type: {item_type}. Use 'poi' or 'obstacle'")


if __name__ == "__main__":
    # Example usage
    print("Example: Adding items to industrial_city.json")
    print("=" * 80)
    
    # Example POI
    add_to_industrial_city(
        "poi",
        "Test Factory",
        local_x=50.0,
        local_y=75.0,
        altitude_meters=25.0,
        type="factory",
        description="Test factory building"
    )
    
    # Example obstacle
    add_to_industrial_city(
        "obstacle",
        "Test Tower",
        local_x=120.0,
        local_y=80.0,
        height_meters=40.0,
        type="tower",
        description="Test tower obstacle"
    )

