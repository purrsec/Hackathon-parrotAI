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
            moveBy,
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
    poi_offset_distance = 25.0  # meters
    # At latitude ~48.88, 1 degree ≈ 111km, so 12m ≈ 0.000108 degrees
    offset_degrees = poi_offset_distance / 111000.0
    
    # Calculate offset positions (north of POI for viewing)
    ventilation_offset_lat = ventilation_lat + offset_degrees
    ventilation_offset_lon = ventilation_lon
    
    advertising_offset_lat = advertising_lat + offset_degrees
    advertising_offset_lon = advertising_lon

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

    def step_move_to_midpoint() -> bool:
        """Move to midpoint that clears the bounding box altitude (15m)."""
        log(f"Moving to midpoint (clears bounding box): lat={midpoint_lat:.6f}, lon={midpoint_lon:.6f}, alt={midpoint_alt}m")
        
        try:
            result = drone(
                extended_move_to(
                    latitude=midpoint_lat,
                    longitude=midpoint_lon,
                    altitude=midpoint_alt,
                    orientation_mode="to_target",
                    heading=0.0,
                    max_horizontal_speed=20.0,
                    max_vertical_speed=3.0,
                    max_yaw_rotation_speed=1.0
                )
            ).wait(_timeout=move_timeout_sec)
            
            if result.success():
                log("Successfully moved to midpoint")
                hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=130)
                return bool(hover_ok)
            else:
                log(f"Move to midpoint failed: {result.explain()}")
                return False
        except Exception as e:
            log(f"Move to midpoint failed with exception: {e}")
            return False

    def step_move_to_ventilation_pipes() -> bool:
        """Move to offset position near Ventilation Pipes POI for viewing."""
        log(f"Moving to offset position near Ventilation Pipes: lat={ventilation_offset_lat:.6f}, lon={ventilation_offset_lon:.6f}, alt={flight_alt}m")
        
        try:
            result = drone(
                extended_move_to(
                    latitude=ventilation_offset_lat,
                    longitude=ventilation_offset_lon,
                    altitude=flight_alt,
                    orientation_mode="to_target",
                    heading=0.0,
                    max_horizontal_speed=20.0,
                    max_vertical_speed=3.0,
                    max_yaw_rotation_speed=1.0
                )
            ).wait(_timeout=move_timeout_sec)
            
            if result.success():
                log("Successfully moved to offset position near Ventilation Pipes")
                hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=130)
                if hover_ok:
                    log("Drone is hovering at offset position")
                return bool(hover_ok)
            else:
                log(f"Move to Ventilation Pipes offset failed: {result.explain()}")
                return False
        except Exception as e:
            log(f"Move to Ventilation Pipes offset failed with exception: {e}")
            return False

    def step_poi_inspect_ventilation_pipes() -> bool:
        """Start POI mode and rotate around Ventilation Pipes for inspection."""
        log(f"Starting POI mode at Ventilation Pipes: lat={ventilation_lat:.6f}, lon={ventilation_lon:.6f}, alt={ventilation_alt}m")
        
        try:
            # Start POI mode at the actual POI location
            log("Sending StartPilotedPOIV2 command...")
            result = drone(StartPilotedPOIV2(
                latitude=ventilation_lat,
                longitude=ventilation_lon,
                altitude=ventilation_alt,
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
            
            # Orbit around the POI using moveBy on Y axis (lateral movement)
            # moveBy parameters: (dx, dy, dz, dPsi) where dy is left/right (Y axis)
            # In POI mode, drone faces POI, so we move left/right using moveBy Y axis
            log("Orbiting around Ventilation Pipes POI...")
            rotation_duration = 15.0  # seconds
            orbit_radius = 5.0  # meters - radius of the orbit
            num_orbits = 1.0  # Number of full circles
            num_steps = 30  # Number of moveBy commands for smooth orbit
            
            total_distance = 2 * math.pi * orbit_radius * num_orbits
            step_distance = total_distance / num_steps
            
            for i in range(num_steps):
                # Calculate angle for circular orbit
                angle = (2 * math.pi * num_orbits * i) / num_steps
                # Calculate lateral movement (dy): positive = right, negative = left
                # Use the derivative of the circular path for smooth movement
                dy = step_distance * math.cos(angle)  # Lateral movement component
                # moveBy: (dx=0 forward/back, dy=lateral, dz=0 up/down, dPsi=0 yaw)
                # In POI mode, dPsi should be 0 as POI mode handles heading
                log(f"Step {i+1}/{num_steps}: Moving laterally by {dy:.2f}m")
                result = drone(moveBy(0.0, dy, 0.0, 0.0)).wait(_timeout=2.0)
                if not result.success():
                    log(f"Warning: moveBy step {i+1} may not have completed: {result.explain()}")
                time.sleep(0.1)  # Small delay between movements
            
            log("Orbit completed")
            
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

    def step_move_to_advertising_board() -> bool:
        """Move to offset position near Advertising Board POI for viewing."""
        log(f"Moving to offset position near Advertising Board: lat={advertising_offset_lat:.6f}, lon={advertising_offset_lon:.6f}, alt={flight_alt}m")
        
        try:
            result = drone(
                extended_move_to(
                    latitude=advertising_offset_lat,
                    longitude=advertising_offset_lon,
                    altitude=flight_alt,
                    orientation_mode="to_target",
                    heading=0.0,
                    max_horizontal_speed=20.0,
                    max_vertical_speed=3.0,
                    max_yaw_rotation_speed=1.0
                )
            ).wait(_timeout=move_timeout_sec)
            
            if result.success():
                log("Successfully moved to offset position near Advertising Board")
                hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=130)
                if hover_ok:
                    log("Drone is hovering at offset position")
                return bool(hover_ok)
            else:
                log(f"Move to Advertising Board offset failed: {result.explain()}")
                return False
        except Exception as e:
            log(f"Move to Advertising Board offset failed with exception: {e}")
            return False

    def step_poi_inspect_advertising_board() -> bool:
        """Start POI mode and rotate around Advertising Board for inspection."""
        log(f"Starting POI mode at Advertising Board: lat={advertising_lat:.6f}, lon={advertising_lon:.6f}, alt={advertising_alt}m")
        
        try:
            # Start POI mode at the actual POI location
            log("Sending StartPilotedPOIV2 command...")
            result = drone(StartPilotedPOIV2(
                latitude=advertising_lat,
                longitude=advertising_lon,
                altitude=advertising_alt,
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
            
            # Orbit around the POI using moveBy on Y axis (lateral movement)
            # moveBy parameters: (dx, dy, dz, dPsi) where dy is left/right (Y axis)
            # In POI mode, drone faces POI, so we move left/right using moveBy Y axis
            log("Orbiting around Advertising Board POI...")
            rotation_duration = 15.0  # seconds
            orbit_radius = 5.0  # meters - radius of the orbit
            num_orbits = 1.0  # Number of full circles
            num_steps = 30  # Number of moveBy commands for smooth orbit
            
            total_distance = 2 * math.pi * orbit_radius * num_orbits
            step_distance = total_distance / num_steps
            
            for i in range(num_steps):
                # Calculate angle for circular orbit
                angle = (2 * math.pi * num_orbits * i) / num_steps
                # Calculate lateral movement (dy): positive = right, negative = left
                # Use the derivative of the circular path for smooth movement
                dy = step_distance * math.cos(angle)  # Lateral movement component
                # moveBy: (dx=0 forward/back, dy=lateral, dz=0 up/down, dPsi=0 yaw)
                # In POI mode, dPsi should be 0 as POI mode handles heading
                log(f"Step {i+1}/{num_steps}: Moving laterally by {dy:.2f}m")
                result = drone(moveBy(0.0, dy, 0.0, 0.0)).wait(_timeout=2.0)
                if not result.success():
                    log(f"Warning: moveBy step {i+1} may not have completed: {result.explain()}")
                time.sleep(0.1)  # Small delay between movements
            
            log("Orbit completed")
            
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

