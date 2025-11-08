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
        from olympe.messages.ardrone3.Piloting import (
            TakeOff,
            Landing,
            NavigateHome,
            StartPilotedPOIV2,
            StopPilotedPOI,
            PCMD,
        )
        from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, PilotedPOI
        from olympe.messages.ardrone3.SpeedSettings import MaxVerticalSpeed, MaxRotationSpeed
        from olympe.messages.move import extended_move_to, extended_move_by
        import time
    except Exception as exc:
        log(f"Olympe import failed: {exc}")
        return EXIT_IMPORT_ERROR

    # Configuration
    drone_ip = os.environ.get("DRONE_IP", "10.202.0.1")
    timeout_sec = float(os.environ.get("TIMEOUT_SEC", "60"))
    safe_altitude_m = float(os.environ.get("SAFE_ALT_M", "35.0"))
    poi_name = os.environ.get("POI_NAME", "Ventilation Pipes")
    poi_offset_m = float(os.environ.get("POI_OFFSET_M", "25.0"))  # Offset distance in meters (north of POI)
    rotation_duration_s = float(os.environ.get("ROTATION_DURATION_S", "30.0"))  # Rotation duration around POI
    
    log("=" * 80)
    log(f"Configuration:")
    log(f"  Drone IP: {drone_ip}")
    log(f"  Timeout: {timeout_sec}s")
    log(f"  Safe altitude: {safe_altitude_m}m")
    log(f"  Target POI: {poi_name}")
    log(f"  POI offset: {poi_offset_m}m (viewing distance)")
    log(f"  Rotation duration: {rotation_duration_s}s")
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

    def step_climb_35m() -> bool:
        from olympe.messages.ardrone3.PilotingState import AltitudeChanged
        import time

        # Ensure speed settings allow our requested per-move caps
        if not drone(MaxVerticalSpeed(4.0)).wait(_timeout=timeout_sec).success():
            log("Failed to set max vertical speed to 4.0 m/s")
            return False
        if not drone(MaxRotationSpeed(90.0)).wait(_timeout=timeout_sec).success():
            log("Failed to set max rotation speed to 90 deg/s")
            return False

        # Determine current altitude and target delta to reach absolute safe_altitude_m
        state = drone.get_state(AltitudeChanged)
        current_alt = state.get("altitude", 0.0) if state is not None else 0.0
        if current_alt >= safe_altitude_m - 0.5:
            log(f"Already at or above safe altitude ({current_alt:.1f}m)")
            return True

        climb_delta = max(0.5, safe_altitude_m - current_alt)
        log(f"Climbing from {current_alt:.1f}m to {safe_altitude_m:.1f}m "
            f"(delta {climb_delta:.1f}m) with max vertical speed 4 m/s...")

        # Send the move and wait briefly for ack; completion is checked by polling altitude
        ack_ok = drone(
            extended_move_by(
                d_x=0.0,
                d_y=0.0,
                d_z=-climb_delta,               # negative is up
                d_psi=0.0,
                max_horizontal_speed=0.5,
                max_vertical_speed=4.0,
                max_yaw_rotation_speed=20.0
            )
        ).wait(_timeout=5).success()
        if not ack_ok:
            log("Warning: climb command ack failed or was refused; continuing to monitor altitude")

        # Poll altitude until reaching the target or timeout
        target_alt = safe_altitude_m
        deadline = time.monotonic() + max(timeout_sec * 3, 120.0)
        last_report = time.monotonic()
        while time.monotonic() < deadline:
            state = drone.get_state(AltitudeChanged)
            if state is not None:
                current_alt = state.get("altitude", current_alt)
            if current_alt >= target_alt - 0.5:
                log(f"✓ Reached {current_alt:.1f}m (>= {target_alt:.1f}m)")
                # Optional: wait a short time for hover stabilization
                drone(FlyingStateChanged(state="hovering", _timeout=10)).wait()
                return True
            now = time.monotonic()
            if now - last_report > 2.0:
                log(f"  Altitude: {current_alt:.1f}m / {target_alt:.1f}m")
                last_report = now
            time.sleep(0.2)

        log(f"Failed to climb to {safe_altitude_m}m (last altitude {current_alt:.1f}m)")
        return False

    def step_goto_poi() -> bool:
        """Move to offset position near the POI for optimal viewing angle."""
        # Calculate offset position (north of the POI)
        # At latitude ~48.88, 1 degree ≈ 111km, so convert meters to degrees
        offset_degrees = poi_offset_m / 111000.0
        offset_lat = target_lat + offset_degrees  # Offset north
        offset_lon = target_lon  # No longitude offset
        
        log(f"Navigating to offset position near POI '{poi_name}'...")
        log(f"  POI location: lat={target_lat:.8f}, lon={target_lon:.8f}, alt={target_alt}m")
        log(f"  Offset position: lat={offset_lat:.8f}, lon={offset_lon:.8f}, alt={safe_altitude_m}m")
        log(f"  Offset distance: {poi_offset_m}m north of POI")
        
        result = drone(
            extended_move_to(
                latitude=offset_lat,
                longitude=offset_lon,
                altitude=safe_altitude_m,
                orientation_mode="to_target",
                heading=0.0,
                max_horizontal_speed=20.0,
                max_vertical_speed=3.0,
                max_yaw_rotation_speed=1.0
            )
        ).wait(_timeout=max(timeout_sec * 3, 180))
        
        if not result.success():
            log(f"Failed to reach offset position near POI '{poi_name}'")
            return False
        
        log(f"✓ Reached offset position near POI '{poi_name}'!")
        
        # Wait for hovering state
        hover_ok = drone(FlyingStateChanged(state="hovering", _timeout=30)).wait().success()
        if not hover_ok:
            log("Warning: Not in hovering state after move")
        
        return True
    
    def step_return_home() -> bool:
        log("Returning to takeoff position...")
        from olympe.messages.ardrone3.Piloting import NavigateHome
        
        result = drone(NavigateHome(start=1)).wait(_timeout=timeout_sec * 3).success()
        
        if not result:
            log("Failed to return home")
            return False
        
        log("✓ Returned to takeoff position")
        return True

    def step_poi_inspect() -> bool:
        """Start POI mode and rotate around the POI for inspection."""
        log(f"Starting POI mode at '{poi_name}': lat={target_lat:.8f}, lon={target_lon:.8f}, alt={target_alt}m")
        
        try:
            # Start POI mode at the actual POI location (not the offset position)
            log("Sending StartPilotedPOIV2 command...")
            result = drone(StartPilotedPOIV2(
                latitude=target_lat,
                longitude=target_lon,
                altitude=target_alt,
                mode="locked_gimbal"  # Keep gimbal locked on POI
            )).wait(_timeout=5)
            
            if not result.success():
                log(f"StartPilotedPOIV2 command failed: {result.explain()}")
                return False
            
            log("✓ POI mode started successfully")
            time.sleep(1)  # Give it time to activate
            
            # Check POI state
            try:
                poi_state = drone.get_state(PilotedPOI)
                if poi_state:
                    log(f"POI state: {poi_state}")
            except Exception:
                log("WARNING: POI state unavailable")
            
            # Rotate around the POI using PCMD with constant roll
            # PCMD parameters: (flag, roll, pitch, yaw, gaz, timestampAndSeqNum)
            # In POI mode, drone faces POI, so we use constant roll to strafe around it
            log(f"Rotating around '{poi_name}' POI for {rotation_duration_s}s...")
            roll_rate = 100  # Roll rate (0-100)
            command_rate_hz = 20  # Commands per second
            rotation_steps = int(rotation_duration_s * command_rate_hz)
            sleep_time = 1.0 / command_rate_hz
            
            for i in range(rotation_steps):
                # Send constant roll command
                drone(PCMD(1, roll_rate, 0, 0, 0, timestampAndSeqNum=0))
                time.sleep(sleep_time)
            
            # Stop movement
            drone(PCMD(0, 0, 0, 0, 0, timestampAndSeqNum=0))
            log("✓ Rotation completed")
            
            # Stop POI mode
            log("Stopping POI mode...")
            try:
                drone(StopPilotedPOI()).wait(_timeout=5)
                log("✓ POI mode stopped")
            except Exception as e:
                log(f"POI stop warning: {e}")
            
            return True
        except Exception as e:
            log(f"POI inspection failed with exception: {e}")
            # Try to stop POI mode even if there was an error
            try:
                drone(StopPilotedPOI()).wait(_timeout=5)
            except Exception:
                pass
            return False

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
        ("climb_35m", step_climb_35m),
        ("goto_poi", step_goto_poi),
        ("poi_inspect", step_poi_inspect),
        ("return_home", step_return_home),
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

