# Simplified World Map Schema for LLM-Driven Drone Control

This document describes a simplified world description focused on **static environment elements** and the **starting position** of the drone. This is designed to be a reusable map/environment definition.

## Overview

The world map is a JSON object that provides:
1. **Starting Position**: Initial drone position
2. **Points of Interest (POIs)**: Landmarks and important locations
3. **Boundaries**: Geofences, no-fly zones, and restrictions
4. **Obstacles**: Static structures (buildings, towers, etc.)
5. **Location Context**: Basic location information

## Schema Structure

```json
{
  "name": "Paris - Tour Eiffel Area",
  "description": "Example map for Paris with Tour Eiffel and basic boundaries",
  
  "starting_position": {
    "coordinates": {
      "latitude": 48.8566,
      "longitude": 2.3522,
      "altitude_meters": 0.0
    },
    "description": "Starting position near Champs de Mars"
  },
  
  "location": {
    "name": "Paris, France",
    "country": "FR",
    "terrain_type": "urban",
    "elevation_meters": 35.0
  },
  
  "points_of_interest": [
    {
      "name": "Tour Eiffel",
      "type": "landmark",
      "coordinates": {
        "latitude": 48.8584,
        "longitude": 2.2945,
        "altitude_meters": 0.0
      },
      "height_meters": 330.0,
      "description": "Eiffel Tower - iconic Paris landmark"
    }
  ],
  
  "boundaries": [
    {
      "name": "Central Paris Geofence",
      "type": "geofence",
      "boundary_type": "polygon",
      "coordinates": [
        [48.85, 2.35],
        [48.86, 2.35],
        [48.86, 2.36],
        [48.85, 2.36]
      ],
      "max_altitude_meters": 50.0,
      "description": "Geofence boundary for central Paris area"
    }
  ],
  
  "obstacles": [
    {
      "name": "High-rise Building",
      "type": "building",
      "coordinates": {
        "latitude": 48.8570,
        "longitude": 2.3530,
        "altitude_meters": 0.0
      },
      "height_meters": 80.0,
      "description": "Tall building in the area"
    }
  ],
  
  "default_max_altitude_meters": 60.0,
  "default_max_distance_meters": 2000.0
}
```

## Field Descriptions

### Starting Position
- **coordinates**: Initial GPS position where the drone starts
- **description**: Optional description of the starting location

### Points of Interest (POIs)
- **name**: Name of the POI (used by LLM to reference it)
- **type**: Type of POI (landmark, building, structure, etc.)
- **coordinates**: GPS position
- **height_meters**: Height of the structure (optional)
- **description**: Optional description

### Boundaries
- **name**: Name of the boundary
- **type**: `geofence`, `no_fly_zone`, or `restricted`
- **boundary_type**: `polygon` or `circle`
- **coordinates**: 
  - For polygon: `[[lat, lon], [lat, lon], ...]` (list of vertices)
  - For circle: `[[center_lat, center_lon], [radius_meters]]`
- **max_altitude_meters**: Maximum allowed altitude within this boundary
- **min_altitude_meters**: Minimum allowed altitude (optional)
- **description**: Optional description

### Obstacles
- **name**: Name of the obstacle
- **type**: Type (building, tower, structure, etc.)
- **coordinates**: GPS position
- **height_meters**: Height of the obstacle
- **description**: Optional description

## Usage Examples

### Load from JSON File

```python
import json
from core.world_map import load_world_map

# Load map
world_map = load_world_map("maps/paris.json")

# Convert to JSON string for LLM
world_map_json = json.dumps(world_map, indent=2)
```

### Use in LLM Prompt

```python
import json
from core.world_map import load_world_map

# Load map
world_map = load_world_map("maps/paris.json")
world_map_json = json.dumps(world_map, indent=2)

# Generate prompt
prompt = f"""
You are a drone mission planner. Given the world map, generate flight instructions.

World Map:
{world_map_json}

Starting Position: ({world_map['starting_position']['coordinates']['latitude']}, {world_map['starting_position']['coordinates']['longitude']})

User Request: {user_input}

Generate Mission DSL JSON that:
1. Uses POI names from the map (e.g., "Tour Eiffel")
2. Respects all boundaries
3. Accounts for obstacles
"""
```

## Example Map Files

### Paris Example

```json
{
  "name": "Paris - Tour Eiffel Area",
  "starting_position": {
    "coordinates": {
      "latitude": 48.8566,
      "longitude": 2.3522,
      "altitude_meters": 0.0
    }
  },
  "points_of_interest": [
    {
      "name": "Tour Eiffel",
      "type": "landmark",
      "coordinates": {
        "latitude": 48.8584,
        "longitude": 2.2945,
        "altitude_meters": 0.0
      },
    }
  ],
  "boundaries": [
    {
      "name": "Central Paris Geofence",
      "type": "geofence",
      "boundary_type": "polygon",
      "coordinates": [
        [48.85, 2.35],
        [48.86, 2.35],
        [48.86, 2.36],
        [48.85, 2.36]
      ],
      "max_altitude_meters": 50.0
    }
  ]
}
```

## Benefits

1. **Simple and Focused**: Only static environment elements, no dynamic state
2. **Reusable**: Maps can be saved and loaded for different missions
3. **LLM-Friendly**: Clear structure that LLMs can easily understand
4. **Easy to Define**: Can be created programmatically or from JSON files

## Integration

This simplified world map can be combined with real-time drone state when needed:

```python
# Static map
world_map = WorldMapBuilder.from_json("maps/paris.json")

# Add current drone state (if needed)
current_position = get_drone_position()  # From Olympe

# Combine in LLM prompt
prompt = f"""
World Map: {world_map.model_dump_json()}
Current Position: {current_position}
User Request: {user_input}
"""
```
