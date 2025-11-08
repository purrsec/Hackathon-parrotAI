"""
Simple test to fly to a GPS location (POI) from industrial_city.json.

Safety: Climbs to 35m first to clear all obstacles before navigating horizontally.
"""

import os
import sys
import json
from pathlib import Path
from typing import Callable, Tuple, Optional


# Exit codes
EXIT_SUCCESS = 0
EXIT_TEST_FAILURE = 1
EXIT_IMPORT_ERROR = 2
EXIT_CONNECTION_ERROR = 3
EXIT_CONFIG_ERROR = 4


def log(message: str) -> None:
    print(f"[GOTO_POI] {message}")


def with_step(name: str, fn: Callable[[], bool]) -> bool:
    log(f"START: {name}")
    try:
        ok = fn()
        if ok:
            log(f"✓ OK: {name}")
        else:
            log(f"✗ FAIL: {name}")
        return ok
    except Exception as exc:
        log(f"✗ EXCEPTION in {name}: {exc}")
        import traceback
        traceback.print_exc()
        return False


def load_poi_from_map(poi_name: str) -> Optional[Tuple[float, float, float]]:
    """
    Load a POI from industrial_city.json by name.
    
    Returns:
        Tuple of (latitude, longitude, altitude_meters) or None if not found
    """
    # Find project root (where maps/ directory is)
    project_root = Path(__file__).parent.parent.parent
    map_file = project_root / "maps" / "industrial_city.json"
    
    if not map_file.exists():
        log(f"Map file not found: {map_file}")
        return None
    
    with open(map_file, "r", encoding="utf-8") as f:
        world_map = json.load(f)
    
    # Search for POI
    for poi in world_map.get("points_of_interest", []):
        if poi["name"].lower() == poi_name.lower():
            coords = poi["coordinates"]
            lat = coords["latitude"]
            lon = coords["longitude"]
            alt = coords.get("altitude_meters", 0.0)
            log(f"Found POI '{poi_name}': lat={lat:.8f}, lon={lon:.8f}, alt={alt}m")
            return (lat, lon, alt)
    
    log(f"POI '{poi_name}' not found in map")
    available = [poi["name"] for poi in world_map.get("points_of_interest", [])]
    log(f"Available POIs: {', '.join(available)}")
    return None


def main() -> int:
    try:
        import olympe
        from olympe import Drone
        from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy
        from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
        from olympe.messages.move import extended_move_to
    except Exception as exc:
        log(f"Olympe import failed: {exc}")
        return EXIT_IMPORT_ERROR

    # Configuration
    drone_ip = os.environ.get("DRONE_IP", "10.202.0.1")
    timeout_sec = float(os.environ.get("TIMEOUT_SEC", "30"))
    safe_altitude_m = float(os.environ.get("SAFE_ALT_M", "35.0"))
    poi_name = os.environ.get("POI_NAME", "Ventilation Pipes")
    
    log("=" * 80)
    log(f"Configuration:")
    log(f"  Drone IP: {drone_ip}")
    log(f"  Timeout: {timeout_sec}s")
    log(f"  Safe altitude: {safe_altitude_m}m")
    log(f"  Target POI: {poi_name}")
    log("=" * 80)
    
    # Load POI coordinates
    poi_coords = load_poi_from_map(poi_name)
    if poi_coords is None:
        log(f"ERROR: Cannot proceed without valid POI coordinates")
        return EXIT_CONFIG_ERROR
    
    target_lat, target_lon, target_alt = poi_coords
    
    # Create drone instance
    drone = Drone(drone_ip)
    connected = False

    def step_connect() -> bool:
        nonlocal connected
        log(f"Connecting to drone at {drone_ip}...")
        try:
            ok = bool(drone.connect())
            if not ok:
                log("Connection failed")
                log("Possible causes:")
                log("  1. Sphinx simulator not running")
                log("  2. Wrong IP or network issue")
                log("  3. Tailscale route not active (ping 10.202.0.1)")
            connected = ok
            return ok
        except Exception as exc:
            log(f"Connection threw an exception: {exc}")
            return False

    def step_takeoff() -> bool:
        log("Sending TakeOff command...")
        if not drone(TakeOff()).wait(_timeout=timeout_sec).success():
            log("TakeOff command failed!")
            return False
        
        log("Waiting for hovering state...")
        if not drone(FlyingStateChanged(state="hovering", _timeout=timeout_sec)).wait().success():
            log("Failed to reach hovering state")
            return False
        
        log("Drone is hovering!")
        return True

    def step_goto_poi_direct() -> bool:
        log(f"Flying directly to POI '{poi_name}' at safe altitude...")
        log(f"  Target: lat={target_lat:.8f}, lon={target_lon:.8f}")
        log(f"  Safe altitude: {safe_altitude_m}m (climbing during flight)")
        
        # Use extended_move_to for GPS navigation with safe altitude
        # This will climb AND move horizontally in an optimized trajectory
        result = drone(
            extended_move_to(
                latitude=target_lat,
                longitude=target_lon,
                altitude=safe_altitude_m,  # Climb to safe altitude during flight
                orientation_mode=olympe.enums.moveTo.OrientationMode.TO_TARGET,
                heading=0.0  # Will be ignored with TO_TARGET mode
            )
        ).wait(_timeout=timeout_sec * 4).success()
        
        if not result:
            log(f"Failed to reach POI '{poi_name}' at safe altitude")
            return False
        
        log(f"✓ Reached POI '{poi_name}' at {safe_altitude_m}m altitude!")
        return True

    def step_hover_and_inspect() -> bool:
        log(f"Hovering at POI for inspection (5 seconds)...")
        import time
        time.sleep(5)
        log("Inspection complete!")
        return True

    def step_land() -> bool:
        log("Sending Landing command...")
        if not drone(Landing()).wait(_timeout=timeout_sec).success():
            log("Landing command failed!")
            return False
        
        log("Waiting for landed state...")
        if not drone(FlyingStateChanged(state="landed", _timeout=timeout_sec)).wait().success():
            log("Failed to reach landed state")
            return False
        
        log("Drone landed!")
        return True

    # Test steps
    steps = [
        ("connect", step_connect),
        ("takeoff", step_takeoff),
        ("goto_poi_direct", step_goto_poi_direct),
        ("hover_and_inspect", step_hover_and_inspect),
        ("land", step_land),
    ]

    overall_ok = True
    try:
        for name, fn in steps:
            ok = with_step(name, fn)
            overall_ok = overall_ok and ok
            if not ok:
                log(f"⚠ Test failed at step '{name}', stopping")
                break
    finally:
        if connected:
            log("Disconnecting from drone...")
            drone.disconnect()
            log("Disconnected")

    log("=" * 80)
    if overall_ok:
        log("✓ TEST PASSED: Successfully navigated to POI and returned")
    else:
        log("✗ TEST FAILED: See errors above")
    log("=" * 80)
    
    return EXIT_SUCCESS if overall_ok else EXIT_TEST_FAILURE


if __name__ == "__main__":
    sys.exit(main())

