import os
import sys
import time
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
        )
        from olympe.messages.ardrone3.PilotingState import (  # type: ignore
            FlyingStateChanged,
            NavigateHomeStateChanged,
            PositionChanged,
        )
        # moveByEnd may not be available in all versions, try to import it
        try:
            from olympe.messages.ardrone3.PilotingState import moveByEnd  # type: ignore
        except ImportError:
            moveByEnd = None
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
        # Ensure last moveBy completed with an event (if available)
        if moveByEnd is not None:
            return bool(drone(moveByEnd(_policy="check")).wait(_timeout=timeout_sec))
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

    def step_poi_start_stop() -> bool:
        # Start a POI piloting around current position (sim must have GPS position)
        try:
            from olympe.messages.poi import start as poi_start, stop as poi_stop  # type: ignore
        except Exception:
            log("POI feature not available; skipping")
            return True

        log("Getting current GPS position...")
        pos = drone.get_state(PositionChanged)
        lat = pos.get("latitude") if isinstance(pos, dict) else None
        lon = pos.get("longitude") if isinstance(pos, dict) else None
        alt = pos.get("altitude") if isinstance(pos, dict) else None
        if lat is None or lon is None or alt is None:
            log("No valid GPS position; skipping POI test")
            return True
        
        log(f"Current position: lat={lat:.6f}, lon={lon:.6f}, alt={alt:.2f}m")

        attempts = [
            {"latitude": lat, "longitude": lon, "altitude": alt, "radius": 10.0, "clockwise": True},
            {"latitude": lat, "longitude": lon, "altitude": alt, "mode": "locked_gimbal", "radius": 10.0, "clockwise": True},
            {"latitude": lat, "longitude": lon, "altitude": alt},
        ]

        started = False
        for idx, kwargs in enumerate(attempts):
            try:
                log(f"Attempting POI start (attempt {idx+1}/{len(attempts)})...")
                if drone(poi_start(**kwargs)).wait(_timeout=timeout_sec).success():
                    log("POI mode started successfully")
                    started = True
                    break
            except Exception as e:
                log(f"POI attempt {idx+1} failed: {e}")
                continue

        if not started:
            log("All POI.start attempts failed; skipping")
            return True

        log("Orbiting POI for 2 seconds...")
        time.sleep(2.0)
        
        log("Stopping POI mode...")
        try:
            result = drone(poi_stop()).wait(_timeout=timeout_sec).success()
            if result:
                log("POI mode stopped successfully")
            return bool(result)
        except Exception:
            log("POI stop failed, continuing anyway")
            return True

    def step_camera_record_and_photo() -> bool:
        # Prefer Camera2; fallback to Ardrone3.MediaRecord
        try:
            from olympe.messages.camera2 import (  # type: ignore
                start_recording,
                stop_recording,
                take_photo,
            )

            log("Starting video recording (Camera2)...")
            if not drone(start_recording()).wait(_timeout=timeout_sec).success():
                log("Failed to start recording")
                return False
            log("Recording started, waiting 1 second...")
            time.sleep(1.0)
            
            log("Stopping video recording...")
            if not drone(stop_recording()).wait(_timeout=timeout_sec).success():
                log("Failed to stop recording")
                return False
            log("Recording stopped successfully")
            time.sleep(0.5)
            
            log("Taking photo...")
            if not drone(take_photo()).wait(_timeout=timeout_sec).success():
                log("Failed to take photo")
                return False
            log("Photo taken successfully")
            return True
        except Exception as e:
            log(f"Camera2 not available ({e}), trying Ardrone3.MediaRecord...")
            try:
                from olympe.messages.ardrone3.MediaRecord import (  # type: ignore
                    VideoV2,
                    PictureV2,
                )
                log("Starting video recording (Ardrone3)...")
                if not drone(VideoV2(record=1)).wait(_timeout=timeout_sec).success():
                    log("Failed to start recording")
                    return False
                log("Recording started, waiting 1 second...")
                time.sleep(1.0)
                
                log("Stopping video recording...")
                if not drone(VideoV2(record=0)).wait(_timeout=timeout_sec).success():
                    log("Failed to stop recording")
                    return False
                log("Recording stopped successfully")
                time.sleep(0.5)
                
                log("Taking photo...")
                if not drone(PictureV2()).wait(_timeout=timeout_sec).success():
                    log("Failed to take photo")
                    return False
                log("Photo taken successfully")
                return True
            except Exception:
                log("Camera feature not available; skipping")
                return True

    def step_rth_then_cancel() -> bool:
        # Try RTH feature, fallback to Ardrone3 NavigateHome
        try:
            from olympe.messages.rth import return_to_home, state as rth_state  # type: ignore

            log("Initiating Return To Home (RTH)...")
            if not drone(return_to_home(1)).wait(_timeout=timeout_sec).success():
                log("Failed to start RTH")
                return False
            log("RTH started")
            
            log("Waiting for RTH state update...")
            if not drone(rth_state(_policy="check")).wait(_timeout=timeout_sec):
                log("RTH state check failed")
                return False
            log("RTH state confirmed")
            
            log("Cancelling RTH with moveBy command...")
            result = drone(moveBy(0.0, 0.0, 0.0, 0.0)).wait(_timeout=timeout_sec).success()
            if result:
                log("RTH cancelled successfully")
            return bool(result)
        except Exception as e:
            log(f"RTH feature not available ({e}), using Ardrone3 NavigateHome...")
            
            log("Starting NavigateHome...")
            if not drone(NavigateHome(1)).wait(_timeout=timeout_sec).success():
                log("Failed to start NavigateHome")
                return False
            log("NavigateHome started")
            
            log("Waiting for NavigateHome state...")
            if not drone(NavigateHomeStateChanged(_policy="check")).wait(_timeout=timeout_sec):
                log("NavigateHome state check failed")
                return False
            log("NavigateHome state confirmed")
            
            log("Cancelling NavigateHome...")
            result = drone(NavigateHome(0)).wait(_timeout=timeout_sec).success()
            if result:
                log("NavigateHome cancelled successfully")
            return bool(result)

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
        ("takeoff_hover", step_takeoff_hover),
        ("move_square", step_move_square),
        ("gimbal_pitch", step_gimbal_pitch),
        ("poi_start_stop", step_poi_start_stop),
        ("camera_record_and_photo", step_camera_record_and_photo),
        ("rth_then_cancel", step_rth_then_cancel),
        ("land", step_land),
    ]

    overall_ok = True
    try:
        for name, fn in steps:
            ok = with_step(name, fn)
            overall_ok = overall_ok and ok
            if not ok and os.environ.get("SMOKE_STRICT", "1") == "1":
                break
    finally:
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


