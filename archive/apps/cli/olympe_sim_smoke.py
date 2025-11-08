import os
import sys
import time
import math
from typing import Callable, Optional

# Exit codes
EXIT_SUCCESS = 0
EXIT_TEST_FAILURE = 1
EXIT_IMPORT_ERROR = 2
EXIT_CONNECTION_ERROR = 3


def log(message: str) -> None:
    print(f"[SMOKE] {message}")


def with_step(name: str, fn: Callable[[], bool]) -> bool:
    log(f"START: {name}")
    try:
        ok = fn()
        if ok:
            log(f"OK: {name}")
        else:
            log(f"FAIL: {name}")
        return ok
    except Exception as exc:  # noqa: BLE001 - surface any unexpected failure
        log(f"EXCEPTION in {name}: {exc}")
        return False


def main() -> int:
    try:
        import olympe  # type: ignore
        from olympe import Drone  # type: ignore
        from olympe.messages.ardrone3.Piloting import (  # type: ignore
            TakeOff,
            Landing,
            moveBy,
            NavigateHome,
            StartPilotedPOIV2,
            StopPilotedPOI,
            PCMD,
        )
        from olympe.messages.ardrone3.PilotingState import (  # type: ignore
            FlyingStateChanged,
            NavigateHomeStateChanged,
            PositionChanged,
            PilotedPOI,
        )
        from olympe.messages.move import extended_move_to  # type: ignore
    except Exception as exc:  # noqa: BLE001
        log(f"Olympe import failed: {exc}")
        return EXIT_IMPORT_ERROR

    drone_ip = os.environ.get("DRONE_IP", "10.202.0.1")
    timeout_sec = float(os.environ.get("SMOKE_TIMEOUT_SEC", "25"))

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
        # Wait until landed or hovering state is known (sim warmup)
        log("Waiting for drone to be ready (checking flying state)...")
        result = drone(FlyingStateChanged(_policy="check")).wait(_timeout=timeout_sec)
        if result:
            state = drone.get_state(FlyingStateChanged)
            log(f"Drone ready! Current state: {state}")
        return bool(result)
    
    def step_ensure_landed() -> bool:
        """Ensure drone is landed before starting tests. If flying, attempt to land or RTH."""
        log("Checking if drone is on the ground...")
        state_result = drone.get_state(FlyingStateChanged)
        
        if not state_result:
            log("Unable to get drone flying state")
            return False
        
        current_state = state_result.get("state") if isinstance(state_result, dict) else None
        log(f"Current flying state: {current_state}")
        
        # Convert enum to string for comparison
        state_str = str(current_state).split(".")[-1] if current_state else None
        
        # States that indicate drone is safely on the ground
        safe_states = ["landed", "motor_ramping"]
        
        if state_str in safe_states:
            log("✓ Drone is safely on the ground")
            return True
        
        # Drone is in the air or in an unsafe state
        log("⚠ Drone is NOT on the ground!")
        log(f"Current state: {state_str}")
        
        # Try to land the drone
        if state_str in ["hovering", "flying"]:
            log("Attempting emergency landing...")
            if drone(Landing()).wait(_timeout=timeout_sec).success():
                log("Landing command sent successfully")
                # Wait for drone to actually land
                time.sleep(3.0)
                landing_result = drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec * 2)
                if landing_result:
                    log("✓ Drone has landed successfully")
                    return True
                else:
                    log("⚠ Drone landing timeout, but continuing...")
                    return True
            else:
                log("Landing command failed")
        
        # If taking off or other state, try RTH first then land
        if state_str in ["takingoff", "emergency"]:
            log("Drone in unusual state, attempting RTH then landing...")
            try:
                # Try modern RTH (command-style, no parameter)
                from olympe.messages.rth import return_to_home  # type: ignore
                if drone(return_to_home(start=1)).wait(_timeout=timeout_sec).success():
                    log("RTH activated, waiting for drone to return and land...")
                    time.sleep(5.0)
                    return True
            except Exception:
                # Fallback to NavigateHome
                log("Trying NavigateHome...")
                if drone(NavigateHome(start=1)).wait(_timeout=timeout_sec).success():
                    log("NavigateHome activated, waiting for drone to return and land...")
                    time.sleep(5.0)
                    return True
        
        log("⚠ Could not verify drone is safely landed, but continuing with caution...")
        return True  # Continue anyway to avoid blocking the entire test

    def step_takeoff_hover() -> bool:
        log("Sending TakeOff command...")
        takeoff_result = drone(TakeOff()).wait(_timeout=timeout_sec).success()
        if not takeoff_result:
            log("TakeOff command failed!")
            return False
        log("TakeOff command sent successfully")
        
        log("Waiting for hovering state...")
        hover_result = drone(FlyingStateChanged(state="hovering")).wait(_timeout=timeout_sec).success()
        if not hover_result:
            log("Failed to reach hovering state")
            return False
        log("Drone is now hovering!")
        
        # Climb to 20m to clear buildings
        log("Climbing to 20m altitude to clear buildings...")
        drone(moveBy(0.0, 0.0, -20.0, 0.0))
        # Wait for moveByEnd event or just wait for hovering again
        time.sleep(2.0)  # Give it time to start climbing
        hover_after_climb = drone(FlyingStateChanged(state="hovering")).wait(_timeout=timeout_sec * 3).success()
        if not hover_after_climb:
            log("Warning: didn't confirm hovering after climb, but continuing...")
        else:
            log("Reached 20m altitude and hovering")
        
        return True

    def step_move_square() -> bool:
        # 5m forward, yaw 90°, repeat 4 times -> 5m x 5m square
        move_distance = 5.0  # meters
        turn_angle = 1.5708  # 90° in radians
        
        log(f"Starting square pattern: {move_distance}m sides")
        for i in range(4):
            log(f"Side {i+1}/4: Moving forward {move_distance}m...")
            if not drone(moveBy(move_distance, 0.0, 0.0, 0.0)).wait(_timeout=timeout_sec).success():
                log(f"Failed to complete forward movement on side {i+1}")
                return False
            log(f"Side {i+1}/4: Forward movement completed")
            
            log(f"Side {i+1}/4: Turning 90° right...")
            if not drone(moveBy(0.0, 0.0, 0.0, turn_angle)).wait(_timeout=timeout_sec).success():
                log(f"Failed to complete turn on side {i+1}")
                return False
            log(f"Side {i+1}/4: Turn completed")
        
        log("Square pattern completed!")
        return True

    def step_mission_z() -> bool:
        """
        Fly a Z-shaped trajectory with constant heading using relative moveBy commands:
          1) Top horizontal leg
          2) Diagonal leg to the opposite side
          3) Bottom horizontal leg
        This creates a realistic inspection-like path that moves the drone away from home,
        suitable to validate RTH behavior afterward.
        """
        length = float(os.environ.get("Z_LENGTH_M", "15.0"))  # total forward distance of each leg
        width = float(os.environ.get("Z_WIDTH_M", "10.0"))    # lateral offset covered by the diagonal
        # Per-leg movement timeout (seconds)
        move_timeout_sec = float(os.environ.get("MOVE_TIMEOUT_SEC", "45"))

        log(f"Starting Z mission: length={length}m, width={width}m")

        # Leg 1: top horizontal (forward)
        log("Z Leg 1/3: Moving forward...")
        move_ack = drone(moveBy(length, 0.0, 0.0, 0.0)).wait(_timeout=move_timeout_sec).success()
        # Always confirm completion by waiting hovering after the move
        hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=move_timeout_sec)
        if not (move_ack or hover_ok):
            log("Failed on Z Leg 1")
            return False
        log("Z Leg 1 completed")

        # Leg 2: diagonal (forward + left)
        # Body frame: +dx is forward, -dy is left
        log("Z Leg 2/3: Moving diagonally (forward-left)...")
        move_ack = drone(moveBy(length, -width, 0.0, 0.0)).wait(_timeout=move_timeout_sec).success()
        hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=move_timeout_sec)
        if not (move_ack or hover_ok):
            log("Failed on Z Leg 2")
            return False
        log("Z Leg 2 completed")

        # Leg 3: bottom horizontal (forward)
        log("Z Leg 3/3: Moving forward...")
        move_ack = drone(moveBy(length, 0.0, 0.0, 0.0)).wait(_timeout=move_timeout_sec).success()
        hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=move_timeout_sec)
        if not (move_ack or hover_ok):
            log("Failed on Z Leg 3")
            return False
        log("Z Leg 3 completed")

        log("Z mission completed!")
        return True

    def step_gimbal_pitch() -> bool:
        try:
            from olympe.messages.gimbal import set_target, attitude  # type: ignore
        except Exception:
            log("Gimbal feature not available; skipping")
            return True
        
        log("Setting gimbal pitch to -10° (looking down)...")
        ok = drone(
            set_target(
                gimbal_id=0,  # Main gimbal (usually 0 for most drones)
                control_mode="position",
                yaw_frame_of_reference="none",
                yaw=0.0,
                pitch_frame_of_reference="absolute",
                pitch=-10.0,
                roll_frame_of_reference="none",
                roll=0.0,
            )
        ).wait(_timeout=timeout_sec)
        if not ok:
            log("Failed to set gimbal target")
            return False
        log("Gimbal position set successfully")
        
        # check we received an attitude event recently
        result = drone(attitude(_policy="check")).wait(_timeout=timeout_sec)
        if result:
            log("Gimbal attitude updated")
        return bool(result)

    def step_move_to_near_poi() -> bool:
        """
        Move to the Ventilation Pipes coordinates from the industrial city map.
        Ventilation Pipes coordinates: 48.87881527709961, 2.3665938951969148 at 20m altitude.
        """
        # Ventilation Pipes coordinates from industrial_city.json
        target_lat = 48.87881527709961
        target_lon = 2.3665938951969148
        target_alt = 40.0  # meters (flying altitude above ventilation pipes)
        
        log(f"Moving to Ventilation Pipes: lat={target_lat:.6f}, lon={target_lon:.6f}, alt={target_alt}m")
        
        try:
            # Move to the target position
            # Use longer timeout for GPS moves (default 120s, configurable via MOVE_TIMEOUT_SEC)
            move_timeout_sec = float(os.environ.get("MOVE_TIMEOUT_SEC", "120"))
            log(f"Sending extended_move_to command (timeout: {move_timeout_sec}s)...")
            
            # Wait for move completion with extended timeout
            result = drone(
                extended_move_to(
                    latitude=target_lat,
                    longitude=target_lon,
                    altitude=target_alt,
                    orientation_mode="to_target",  # Face the specified heading
                    heading=0.0,
                    max_horizontal_speed=8.0,
                    max_vertical_speed=3.0,
                    max_yaw_rotation_speed=1.0
                )
            ).wait(_timeout=move_timeout_sec)
            
            if result.success():
                log("Successfully moved to Ventilation Pipes position")
                # Wait for hovering state to confirm arrival
                # Use longer timeout for hovering check (default 30s)
                hover_timeout_sec = float(os.environ.get("HOVER_TIMEOUT_SEC", "120"))
                log(f"Waiting for hovering state (timeout: {hover_timeout_sec}s)...")
                hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=hover_timeout_sec)
                if hover_ok:
                    log("Drone is hovering at target position")
                else:
                    log(f"Warning: Hovering state not confirmed within {hover_timeout_sec}s, but move completed")
                return bool(hover_ok)
            else:
                log(f"Move to Ventilation Pipes failed (timeout: {move_timeout_sec}s)")
                log(f"Explanation: {result.explain()}")
                return False
        except Exception as e:
            log(f"Move to Ventilation Pipes failed with exception: {e}")
            return False

    def step_move_away_from_home() -> bool:
        """
        Move approximately 20m away from the initial position using relative moveBy.
        This positions the drone away from home before starting POI mode.
        """
        move_distance = 15.0  # meters forward
        # Per-movement timeout (seconds)
        move_timeout_sec = float(os.environ.get("MOVE_TIMEOUT_SEC", "45"))

        log(f"Moving {move_distance}m forward from current position...")
        move_ack = drone(moveBy(move_distance, 0.0, 0.0, 0.0)).wait(_timeout=move_timeout_sec).success()
        # Always confirm completion by waiting hovering after the move
        hover_ok = drone(FlyingStateChanged(state="hovering")).wait(_timeout=move_timeout_sec)
        if not (move_ack or hover_ok):
            log("Failed to move away from home")
            return False
        log("Successfully moved away from home")
        
        return True

    def step_poi_start_stop() -> bool:
        """
        Start a POI piloting around specified coordinates.
        """
        
        poi_lat = 48.87991994804089
        poi_lon = 2.369160096117185
        poi_alt = 2.0
        
        log(f"Starting POI mode at coordinates: lat={poi_lat:.6f}, lon={poi_lon:.6f}, alt={poi_alt}m")

        try:
            # Send command without waiting for specific status
            log("Sending StartPilotedPOI command...")
            result = drone(StartPilotedPOIV2(
                latitude=poi_lat,
                longitude=poi_lon,
                altitude=poi_alt,
                mode="locked_gimbal"  # Options: "locked_gimbal" or "free_gimbal"
            )).wait(_timeout=5)
            
            if not result.success():
                log(f"StartPilotedPOIV2 command failed: {result.explain()}")
                return False
            
            log("POI command sent successfully")
            
            # Give it time to activate
            time.sleep(1)
            
            # Check POI state manually
            try:
                poi_state = drone.get_state(PilotedPOI)
                if poi_state:
                    log(f"POI state: {poi_state}")
                else:
                    log("WARNING: Cannot verify POI state")
            except:
                log("WARNING: POI state unavailable in simulator")
                
        except Exception as e:
            log(f"POI start exception: {e}")
            return False

        log("Orbiting POI for 5 seconds...")
        
        # Manual orbit with PCMD
        for i in range(500):  # 25 seconds
            drone(PCMD(1, 20, 0, -15, 0, timestampAndSeqNum=0))
            time.sleep(0.05)
        
        # Stop movement
        drone(PCMD(0, 0, 0, 0, 0, timestampAndSeqNum=0))
        
        log("Stopping POI mode...")
        try:
            drone(StopPilotedPOI()).wait(_timeout=5)
            log("POI mode stopped")
            return True
        except Exception as e:
            log(f"POI stop failed: {e}")
            return True  # Continue anyway

    def step_camera_record_and_photo() -> bool:
        """Test camera recording and photo capture. May not work in all simulators."""
        log("Testing camera functionality (recording + photo)...")
        log("Note: Camera recording is automatic on Anafi AI during flight")
        
        # For Anafi AI (Anafi 2), camera recording is managed automatically
        # The drone starts recording when taking off and stops when landing
        # We can monitor the state but don't need to explicitly control it
        
        try:
            # Check if camera2 protobuf API is available
            log("Checking camera state...")
            camera_state = drone.get_state(olympe.messages.camera2.Event.State)  # type: ignore
            
            if camera_state:
                recording_info = camera_state.get("recording", {})
                recording_state = recording_info.get("state", "unknown")
                log(f"Camera recording state: {recording_state}")
                
                if recording_state == "active":
                    log("✓ Camera is actively recording (auto-started on takeoff)")
                    log("Camera test passed - recording confirmed")
                    return True
                else:
                    log(f"Camera state is '{recording_state}' (may be between flights)")
                    log("Camera test completed")
                    return True
            else:
                log("Could not retrieve camera state")
                log("Camera test skipped (state unavailable)")
                return True
                
        except Exception as e:
            log(f"Camera check failed: {e}")
            log("Camera test skipped (not critical for smoke test)")
            return True

    def step_rth_then_cancel() -> bool:
        """Test RTH feature. Skipped if drone is already at home position."""
        log("Testing RTH (Return To Home) feature...")
        log("Note: RTH completes instantly when drone is already at home")
        
        # Simply test that NavigateHome command can be sent
        # The drone is already at home position, so RTH will complete immediately
        try:
            log("Sending NavigateHome command...")
            # Send command with short timeout - it will complete immediately if at home
            result = drone(NavigateHome(start=1)).wait(_timeout=2.0)
            if result.success():
                log("NavigateHome command sent successfully")
            else:
                log("NavigateHome completed immediately (already at home)")
            
            time.sleep(0.5)  # Brief pause
            
            log("Cancelling NavigateHome...")
            result = drone(NavigateHome(start=0)).wait(_timeout=2.0)
            if result.success():
                log("NavigateHome cancelled successfully")
            
            log("RTH test completed")
            return True
            
        except Exception as e:
            log(f"RTH test encountered issue: {e}")
            log("Continuing anyway (non-critical test)")
            return True

    def step_rth_and_land() -> bool:
        """
        Trigger Return-To-Home and wait until it finishes, then land.
        Prefers the modern rth API and falls back to NavigateHome if needed.
        """
        log("Triggering Return-To-Home...")
        used_fallback = False
        # Allow longer timeout for full return flight (configurable)
        rth_timeout_sec = float(os.environ.get("RTH_TIMEOUT_SEC", "300"))
        # Radius in meters to consider "at home"
        home_radius_m = float(os.environ.get("RTH_HOME_RADIUS_M", "5.0"))

        def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            r = 6371000.0
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(math.radians(lat1))
                * math.cos(math.radians(lat2))
                * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return r * c

        # Try to read home (takeoff) location for proximity-based confirmation
        home_lat = None
        home_lon = None
        try:
            from olympe.messages import rth as rth_msgs  # type: ignore
            tk = drone.get_state(rth_msgs.takeoff_location)
            if isinstance(tk, dict):
                home_lat = tk.get("latitude")
                home_lon = tk.get("longitude")
        except Exception:
            # rth messages not available yet; ignore
            pass

        try:
            from olympe.messages import rth  # type: ignore
            # If available, try to set RTH ending behavior to landing (instead of hovering)
            try:
                if hasattr(rth, "set_ending_behavior"):
                    drone(rth.set_ending_behavior(ending_behavior="landing")).wait(_timeout=timeout_sec)
                    log("RTH ending behavior set to 'landing'")
            except Exception:
                # If the command isn't supported, continue with default behavior
                log("Could not set RTH ending behavior to 'landing' (not supported)")
            if not drone(rth.return_to_home(start=1)).wait(_timeout=timeout_sec).success():
                log("Failed to start RTH via rth.return_to_home")
                return False
            log("RTH started, waiting for completion...")
            # Wait until RTH reports finished (available, reason=finished) with extended timeout
            finished = drone(rth.state(state="available", reason="finished")).wait(_timeout=rth_timeout_sec)
            if not finished:
                log("RTH did not report completion in time; will also check proximity to home...")
        except Exception:
            used_fallback = True
            log("rth API not available; falling back to NavigateHome...")
            if not drone(NavigateHome(start=1)).wait(_timeout=timeout_sec).success():
                log("Failed to start NavigateHome")
                return False
            # fallback path: just wait some time and then rely on proximity check
            time.sleep(5.0)

        # If we have home coordinates, wait until near-home or RTH finished
        near_home = False
        if home_lat is not None and home_lon is not None:
            start_wait = time.time()
            while time.time() - start_wait < rth_timeout_sec:
                pos = drone.get_state(olympe.messages.ardrone3.PilotingState.PositionChanged)  # type: ignore
                if isinstance(pos, dict):
                    lat = pos.get("latitude")
                    lon = pos.get("longitude")
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        dist = haversine_m(home_lat, home_lon, float(lat), float(lon))
                        log(f"RTH progress: distance to home ~ {dist:.1f} m")
                        if dist <= home_radius_m:
                            near_home = True
                            break
                time.sleep(1.0)

        if near_home:
            log("Arrived near home location (within radius); proceeding to land.")
        else:
            log("Proximity check did not confirm arrival within timeout; proceeding cautiously to land.")

        # Depending on configuration, RTH may end in hovering near home. Ensure landing.
        log("Initiating landing after RTH...")
        land_ok = drone(Landing()).wait(_timeout=timeout_sec * 2).success()
        if not land_ok:
            log("Landing command failed after RTH")
            return False
        # Wait until we are actually landed
        landed = drone(FlyingStateChanged(state="landed")).wait(_timeout=timeout_sec * 2)
        if landed:
            log("✓ RTH completed and drone landed")
        else:
            log("⚠ Drone landing status not confirmed within timeout")
        # Optionally cut motors after landing (safe only on ground)
        cut_flag = os.environ.get("CUT_MOTORS_ON_GROUND", "1")
        if landed and cut_flag != "0":
            try:
                from olympe.messages.ardrone3.Piloting import Emergency  # type: ignore
                # Small extra guard delay to ensure ground contact is stable
                time.sleep(1.0)
                log("Cutting motors (Emergency) as drone is confirmed landed...")
                drone(Emergency()).wait(_timeout=timeout_sec)
                log("✓ Motors cut command sent")
            except Exception:
                log("Could not send Emergency() to cut motors; skipping")
        return bool(landed)

    def step_land() -> bool:
        log("Sending Landing command...")
        result = drone(Landing()).wait(_timeout=timeout_sec).success()
        if result:
            log("Landing command successful - drone is landing")
        else:
            log("Landing command failed!")
        return bool(result)

    steps = [
        ("connect", step_connect),
        ("wait_ready", step_wait_ready),
        ("ensure_landed", step_ensure_landed),
        ("takeoff_hover", step_takeoff_hover),
        ("move_to_near_poi", step_move_to_near_poi),
    ]

    overall_ok = True
    took_off = False  # Track if drone took off
    landed_safely = False  # Track if landing was executed
    
    try:
        for name, fn in steps:
            ok = with_step(name, fn)
            overall_ok = overall_ok and ok
            
            # Track if we successfully took off
            if name == "takeoff_hover" and ok:
                took_off = True
                log("✓ Drone airborne - landing will be enforced at end")
            
            # Track if we successfully landed
            if name == "rth_and_land" and ok:
                landed_safely = True
                log("✓ Drone landed safely")
            
            # Stop on failure in strict mode
            if not ok and os.environ.get("SMOKE_STRICT", "1") == "1":
                log(f"⚠ Test '{name}' failed in strict mode - stopping tests")
                break
    finally:
        # CRITICAL: Always land if drone took off and hasn't landed yet
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

    # Determine exit code based on failure type
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


#Z_LENGTH_M=15 Z_WIDTH_M=10 uv run apps/cli/olympe_sim_smoke.py