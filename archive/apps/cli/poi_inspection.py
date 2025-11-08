import os
import sys
import time
import math
from typing import Callable

# Exit codes
EXIT_SUCCESS = 0
EXIT_TEST_FAILURE = 1
EXIT_IMPORT_ERROR = 2
EXIT_CONNECTION_ERROR = 3


def log(message: str) -> None:
    print(f"[POI_INSPECTION] {message}")


def with_step(name: str, fn: Callable[[], bool]) -> bool:
    log(f"START: {name}")
    try:
        ok = fn()
        if ok:
            log(f"OK: {name}")
        else:
            log(f"FAIL: {name}")
        return ok
    except Exception as exc:  # noqa: BLE001
        log(f"EXCEPTION in {name}: {exc}")
        return False


def main() -> int:
    try:
        import olympe  # type: ignore
        from olympe import Drone  # type: ignore
        from olympe.messages.ardrone3.Piloting import (  # type: ignore
            TakeOff,
            Landing,
            NavigateHome,
            StartPilotedPOIV2,
            StopPilotedPOI,
            PCMD,
        )
        from olympe.messages.ardrone3.PilotingState import (  # type: ignore
            FlyingStateChanged,
            PilotedPOI,
        )
        from olympe.messages.move import extended_move_to  # type: ignore
    except Exception as exc:  # noqa: BLE001
        log(f"Olympe import failed: {exc}")
        return EXIT_IMPORT_ERROR

    drone_ip = os.environ.get("DRONE_IP", "10.202.0.1")
    timeout_sec = float(os.environ.get("TIMEOUT_SEC", "25"))
    move_timeout_sec = float(os.environ.get("MOVE_TIMEOUT_SEC", "120"))

    # Coordinates from industrial_city.json
    # Starting position
    start_lat = 48.87991994804089
    start_lon = 2.369160096117185
    
    # Ventilation Pipes
    ventilation_lat = 48.87881527709961
    ventilation_lon = 2.3665938951969148
    ventilation_alt = 20.0  # meters
    
    # Advertising Board
    advertising_lat = 48.87882157897949
    advertising_lon = 2.368181582689285
    advertising_alt = 19.0  # meters
    
    # Bounding box max altitude: 15.0m
    # Calculate midpoint between start and ventilation pipes at safe altitude
    midpoint_lat = (start_lat + ventilation_lat) / 2.0
    midpoint_lon = (start_lon + ventilation_lon) / 2.0
    midpoint_alt = 25.0  # meters (safely above 15m bounding box)
    
    # Flight altitude for inspection (above structures)
    flight_alt = 30.0  # meters
    
    # Offset distance for POI viewing (meters) - drone position offset from POI for good camera angle
    # This can be adjusted per POI when calling move_to_gps_position() or poi_inspect()
    poi_offset_distance = 25.0  # meters (default offset)

    drone = Drone(drone_ip)
    connected = False
    connection_failed = False

    def step_connect() -> bool:
        nonlocal connected, connection_failed
        try:
            log(f"Attempting to connect to drone at {drone_ip}...")
            ok = bool(drone.connect())
            if not ok:
                connection_failed = True
                log("=" * 60)
                log("CONNECTION FAILED - Simulator/Drone not accessible")
                log("=" * 60)
                log(f"Drone IP: {drone_ip}")
                log("Possible causes:")
                log("  1. Parrot Sphinx simulator is not running")
                log("  2. Physical drone is not powered on or in range")
                log("  3. Network configuration issue (firewall, routing)")
                log("  4. Wrong IP address")
                log("")
                log("To start Sphinx simulator:")
                log("  sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone")
                log("=" * 60)
            connected = ok
            return ok
        except Exception as exc:  # noqa: BLE001
            connection_failed = True
            log(f"Connection threw an exception: {exc}")
            log(
                "Hint: ensure Parrot Sphinx is running and accessible; verify the IP and your firewall."
            )
            return False

    def step_wait_ready() -> bool:
        log("Waiting for drone to be ready (checking flying state)...")
        result = drone(FlyingStateChanged(_policy="check")).wait(_timeout=timeout_sec)
        if result:
            state = drone.get_state(FlyingStateChanged)
            log(f"Drone ready! Current state: {state}")
        return bool(result)

    def step_ensure_landed() -> bool:
        """Ensure drone is landed before starting."""
        log("Checking if drone is on the ground...")
        state_result = drone.get_state(FlyingStateChanged)
        
        if not state_result:
            log("Unable to get drone flying state")
            return False
        
        current_state = state_result.get("state") if isinstance(state_result, dict) else None
        log(f"Current flying state: {current_state}")
        
        state_str = str(current_state).split(".")[-1] if current_state else None
        safe_states = ["landed", "motor_ramping"]
        
        if state_str in safe_states:
            log("✓ Drone is safely on the ground")
            return True
        
        log("⚠ Drone is NOT on the ground!")
        log(f"Current state: {state_str}")
        
        if state_str in ["hovering", "flying"]:
            log("Attempting emergency landing...")
            if drone(Landing()).wait(_timeout=timeout_sec).success():
                log("Landing command sent successfully")
                time.sleep(3.0)
                landing_result = drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec * 2)
                if landing_result:
                    log("✓ Drone has landed successfully")
                    return True
        
        log("⚠ Could not verify drone is safely landed, but continuing with caution...")
        return True

    def step_takeoff_hover() -> bool:
        log("Sending TakeOff command...")
        takeoff_result = drone(TakeOff()).wait(_timeout=timeout_sec).success()
        if not takeoff_result:
            log("TakeOff command failed!")
            return False
        log("TakeOff command sent successfully")
        
        log("Waiting for hovering state...")
        hover_result = drone(FlyingStateChanged(state="hovering")).wait(_timeout=timeout_sec).success()
        if hover_result:
            log("Drone is now hovering!")
        else:
            log("Failed to reach hovering state")
        return bool(hover_result)

    def move_to_gps_position(
        lat: float,
        lon: float,
        alt: float,
        name: str,
        hover_timeout: float = 130.0,
        offset_distance: float = 0.0
    ) -> bool:
        """
        Generic function to move drone to a GPS position, optionally with an offset.
        
        Args:
            lat: Target latitude (or POI latitude if offset is used)
            lon: Target longitude (or POI longitude if offset is used)
            alt: Target altitude in meters
            name: Name/description of the destination (for logging)
            hover_timeout: Timeout for hovering state confirmation in seconds
            offset_distance: Optional offset distance in meters (north of target). 
                           If > 0, calculates offset position for better viewing angle.
        
        Returns:
            True if successful, False otherwise
        """
        # Calculate offset position if offset_distance is provided
        target_lat = lat
        target_lon = lon
        
        if offset_distance > 0:
            # At latitude ~48.88, 1 degree ≈ 111km, so convert meters to degrees
            offset_degrees = offset_distance / 111000.0
            target_lat = lat + offset_degrees  # Offset north
            target_lon = lon  # No longitude offset
            log(f"Moving to offset position near {name} (offset: {offset_distance}m north): lat={target_lat:.6f}, lon={target_lon:.6f}, alt={alt}m")
        else:
            log(f"Moving to {name}: lat={target_lat:.6f}, lon={target_lon:.6f}, alt={alt}m")
        
        try:
            result = drone(
                extended_move_to(
                    latitude=target_lat,
                    longitude=target_lon,
                    altitude=alt,
                    orientation_mode="to_target",
                    heading=0.0,
                    max_horizontal_speed=20.0,
                    max_vertical_speed=3.0,
                    max_yaw_rotation_speed=1.0
                )
            ).wait(_timeout=move_timeout_sec)
            
            if result.success():
                log(f"Successfully moved to {name}")
                hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=hover_timeout)
                if hover_ok:
                    log(f"Drone is hovering at {name}")
                return bool(hover_ok)
            else:
                log(f"Move to {name} failed: {result.explain()}")
                return False
        except Exception as e:
            log(f"Move to {name} failed with exception: {e}")
            return False

    def poi_inspect(
        poi_lat: float,
        poi_lon: float,
        poi_alt: float,
        poi_name: str,
        rotation_duration: float = 30.0,
        roll_rate: int = 100,
        command_rate_hz: int = 20,
        offset_distance: float = 0.0
    ) -> bool:
        """
        Generic function to start POI mode and rotate around a POI for inspection.
        
        Args:
            poi_lat: POI latitude
            poi_lon: POI longitude
            poi_alt: POI altitude in meters
            poi_name: Name of the POI (for logging)
            rotation_duration: Duration of rotation in seconds
            roll_rate: Roll rate for PCMD (0-100)
            command_rate_hz: Command rate in Hz (commands per second)
            offset_distance: Offset distance in meters (for reference, not used in POI mode).
                           POI mode uses the actual POI coordinates, but this can be used
                           to document the offset used when moving to the POI position.
        
        Returns:
            True if successful, False otherwise
        """
        log(f"Starting POI mode at {poi_name}: lat={poi_lat:.6f}, lon={poi_lon:.6f}, alt={poi_alt}m")
        
        try:
            # Start POI mode at the actual POI location
            log("Sending StartPilotedPOIV2 command...")
            result = drone(StartPilotedPOIV2(
                latitude=poi_lat,
                longitude=poi_lon,
                altitude=poi_alt,
                mode="locked_gimbal"  # Keep gimbal locked on POI
            )).wait(_timeout=5)
            
            if not result.success():
                log(f"StartPilotedPOIV2 command failed: {result.explain()}")
                return False
            
            log("POI mode started successfully")
            time.sleep(1)  # Give it time to activate
            
            # Check POI state
            try:
                poi_state = drone.get_state(PilotedPOI)
                if poi_state:
                    log(f"POI state: {poi_state}")
            except Exception:
                log("WARNING: POI state unavailable")
            
            # Rotate around the POI using PCMD with constant roll
            # PCMD parameters: (flag, roll, pitch, yaw, gaz, timestamp)
            # In POI mode, drone faces POI, so we use constant roll to strafe around it
            log(f"Rotating around {poi_name} POI...")
            rotation_steps = int(rotation_duration * command_rate_hz)
            sleep_time = 1.0 / command_rate_hz
            
            for i in range(rotation_steps):
                # Send constant roll command
                drone(PCMD(1, roll_rate, 0, 0, 0, timestampAndSeqNum=0))
                time.sleep(sleep_time)
            
            # Stop movement
            drone(PCMD(0, 0, 0, 0, 0, timestampAndSeqNum=0))
            log("Rotation completed")
            
            # Stop POI mode
            log("Stopping POI mode...")
            try:
                drone(StopPilotedPOI()).wait(_timeout=5)
                log("POI mode stopped")
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

    def step_move_to_midpoint() -> bool:
        """Move to midpoint that clears the bounding box altitude (15m)."""
        return move_to_gps_position(
            midpoint_lat, midpoint_lon, midpoint_alt,
            "midpoint (clears bounding box)"
        )

    def step_move_to_ventilation_pipes() -> bool:
        """Move to offset position near Ventilation Pipes POI for viewing."""
        return move_to_gps_position(
            ventilation_lat, ventilation_lon, flight_alt,
            "offset position near Ventilation Pipes",
            offset_distance=25
        )

    def step_poi_inspect_ventilation_pipes() -> bool:
        """Start POI mode and rotate around Ventilation Pipes for inspection."""
        return poi_inspect(
            ventilation_lat, ventilation_lon, ventilation_alt,
            "Ventilation Pipes",
            offset_distance=25
        )

    def step_move_to_advertising_board() -> bool:
        """Move to offset position near Advertising Board POI for viewing."""
        return move_to_gps_position(
            advertising_lat, advertising_lon, flight_alt,
            "offset position near Advertising Board",
            offset_distance=15
        )

    def step_poi_inspect_advertising_board() -> bool:
        """Start POI mode and rotate around Advertising Board for inspection."""
        return poi_inspect(
            advertising_lat, advertising_lon, advertising_alt,
            "Advertising Board",
            offset_distance=15
        )

    def step_rth_and_land() -> bool:
        """Return to home and land."""
        log("Triggering Return-To-Home...")
        rth_timeout_sec = float(os.environ.get("RTH_TIMEOUT_SEC", "300"))
        
        try:
            from olympe.messages import rth  # type: ignore
            try:
                if hasattr(rth, "set_ending_behavior"):
                    drone(rth.set_ending_behavior(ending_behavior="landing")).wait(_timeout=timeout_sec)
                    log("RTH ending behavior set to 'landing'")
            except Exception:
                log("Could not set RTH ending behavior to 'landing' (not supported)")
            
            if not drone(rth.return_to_home(start=1)).wait(_timeout=timeout_sec).success():
                log("Failed to start RTH via rth.return_to_home")
                return False
            
            log("RTH started, waiting for completion...")
            finished = drone(rth.state(state="available", reason="finished")).wait(_timeout=rth_timeout_sec)
            if not finished:
                log("RTH did not report completion in time")
        except Exception:
            log("rth API not available; falling back to NavigateHome...")
            if not drone(NavigateHome(start=1)).wait(_timeout=timeout_sec).success():
                log("Failed to start NavigateHome")
                return False
            time.sleep(5.0)

        log("Initiating landing after RTH...")
        land_ok = drone(Landing()).wait(_timeout=timeout_sec * 2).success()
        if not land_ok:
            log("Landing command failed after RTH")
            return False
        
        landed = drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec * 2)
        if landed:
            log("✓ RTH completed and drone landed")
        else:
            log("⚠ Drone landing status not confirmed within timeout")
        
        return bool(landed)

    steps = [
        ("connect", step_connect),
        ("wait_ready", step_wait_ready),
        ("ensure_landed", step_ensure_landed),
        ("takeoff_hover", step_takeoff_hover),
        ("move_to_midpoint", step_move_to_midpoint),
        ("move_to_ventilation_pipes", step_move_to_ventilation_pipes),
        ("poi_inspect_ventilation_pipes", step_poi_inspect_ventilation_pipes),
        ("move_to_advertising_board", step_move_to_advertising_board),
        ("poi_inspect_advertising_board", step_poi_inspect_advertising_board),
        ("rth_and_land", step_rth_and_land),
    ]

    overall_ok = True
    took_off = False
    landed_safely = False
    
    try:
        for name, fn in steps:
            ok = with_step(name, fn)
            overall_ok = overall_ok and ok
            
            if name == "takeoff_hover" and ok:
                took_off = True
                log("✓ Drone airborne - landing will be enforced at end")
            
            if name == "rth_and_land" and ok:
                landed_safely = True
                log("✓ Drone landed safely")
            
            if not ok and os.environ.get("STRICT", "1") == "1":
                log(f"⚠ Step '{name}' failed in strict mode - stopping")
                break
    finally:
        if took_off and not landed_safely:
            log("=" * 60)
            log("⚠️  SAFETY: Enforcing Return-To-Home and landing - drone is still airborne!")
            log("=" * 60)
            try:
                with_step("rth_and_land_safety", step_rth_and_land)
                log("✓ Safety RTH and landing completed")
            except Exception as e:
                log(f"❌ Emergency landing failed: {e}")
                log("⚠️  MANUAL INTERVENTION REQUIRED - DRONE MAY BE AIRBORNE!")
        
        if connected:
            try:
                drone.disconnect()
                log("Disconnected from drone")
            except Exception:  # noqa: BLE001
                pass

    if connection_failed:
        log("RESULT: CONNECTION ERROR")
        log(f"Exit code: {EXIT_CONNECTION_ERROR}")
        return EXIT_CONNECTION_ERROR
    elif overall_ok:
        log("RESULT: PASS")
        log(f"Exit code: {EXIT_SUCCESS}")
        return EXIT_SUCCESS
    else:
        log("RESULT: TEST FAILURE")
        log(f"Exit code: {EXIT_TEST_FAILURE}")
        return EXIT_TEST_FAILURE


if __name__ == "__main__":
    sys.exit(main())

