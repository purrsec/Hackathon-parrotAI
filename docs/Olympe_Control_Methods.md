Olympe Control Methods Catalog (Parrot ANAFI family)
===================================================

Scope: Commands and key states to control flight, navigation, camera, and mission execution via Olympe eDSL. Grouped by feature. For message semantics and parameters, refer to Parrot’s Olympe documentation.

Primary reference: https://developer.parrot.com/docs/olympe/index.html

Notes
-----

- Names reflect Olympe’s message namespaces. Some features expose CamelCase (Ardrone3) while newer ones use snake_case. Availability depends on drone model/firmware.
- “Commands” are invoked as `drone(Command(...))`; “States/Events” are read via expectations or `drone.get_state(...)`.


Ardrone3.Piloting (core piloting)
----------------------------------

Commands
- TakeOff()
- Landing()
- Emergency()
- moveBy(dx, dy, dz, dPsi)
- CancelMoveBy()
- PCMD(flag, roll, pitch, yaw, gaz, timestamp)
- NavigateHome(start)

States/Events
- FlyingStateChanged(state)
- PositionChanged(latitude, longitude, altitude)
- SpeedChanged(speedX, speedY, speedZ)
- AttitudeChanged(roll, pitch, yaw)
- NavigateHomeStateChanged(state, reason)
- moveByEnd(dX, dY, dZ, dPsi, error)


Move (absolute/extended moves)
-------------------------------

Commands
- move_to(latitude, longitude, altitude, orientation_mode, heading)
- extended_move_to(latitude, longitude, altitude, orientation_mode, heading, max_horizontal_speed, max_vertical_speed, max_yaw_rotation_speed)
- extended_move_by(dX, dY, dZ, dPsi, max_horizontal_speed, max_vertical_speed, max_yaw_rotation_speed)
- cancel_move_to()
- stop()

States/Events
- move_to_changed(status, error)


RTH (Return To Home)
--------------------

Commands
- return_to_home(start)
- set_preferred_home_type(type)
- set_custom_location(latitude, longitude, altitude)
- set_delay(seconds)

States/Events
- state(state)
- home_type(type)
- preferred_home_type(type)
- home_location(latitude, longitude, altitude)
- rth_altitude(altitude)


POI (Point Of Interest)
-----------------------

Commands
- start(latitude, longitude, altitude, mode, heading, clockwise, radius)
- stop()

States/Events
- status(state, error)


PointNFly
---------

Commands
- start(latitude, longitude, altitude, heading_mode, heading)
- stop()

States/Events
- status(state, error)


Flight Plan (Common.Mavlink)
----------------------------

Commands
- SetFlightPlan(flightplan_path, type)
- Start()
- Pause()
- Stop()
- SetSpeed(speed_type, current)

States/Events
- FlightPlanState(state, file)
- MavlinkFilePlayingStateChanged(state, filepath, type)
- MavlinkPlayError(last_error)


Gimbal
------

Commands
- set_target(gimbal_id, control_mode, yaw_frame_of_reference, yaw, pitch_frame_of_reference, pitch, roll_frame_of_reference, roll)
  * gimbal_id: typically 0 for main gimbal
- set_offsets(gimbal_id, yaw, pitch, roll)
- set_max_speed(gimbal_id, yaw, pitch, roll)
- calibrate(gimbal_id)

States/Events
- attitude(gimbal_id, frame_of_reference, yaw_absolute, pitch_absolute, roll_absolute, yaw_relative, pitch_relative, roll_relative)
- state(gimbal_id, mode)
- alert(gimbal_id, error)


Camera / Camera2 (recording, photo, imaging)
---------------------------------------------

Commands (Camera2-style)
- set_mode(cam_id, mode)
- set_recording_mode(cam_id, mode, resolution, framerate, hyperlapse)
- start_recording(cam_id)
  * cam_id: typically 0 for main camera
- stop_recording(cam_id)
- set_photo_mode(cam_id, mode, format, file_format)
- take_photo(cam_id, bracketing, burst_value, capture_interval)
- set_white_balance(cam_id, mode, custom_temperature)
- set_ev_compensation(cam_id, value)
- set_exposure_settings(cam_id, mode, shutter_speed, iso_sensitivity, maximum_iso_sensitivity, metering_mode)
- set_zoom_target(cam_id, control_mode, target)
- set_zoom_velocity(cam_id, velocity)
- set_alignment(cam_id, horizon, yaw)

States/Events
- recording_state(cam_id, state, start_stop_error)
- photo_state(cam_id, state, error)
- zoom_level(cam_id, current_level)
- white_balance(cam_id, mode)
- ev_compensation(cam_id, value)


Common.Settings (selected controls)
-----------------------------------

Commands
- MaxAltitude(current)
- MaxDistance(current)
- NoFlyOverMaxDistance(shouldNotFlyOver)
- BankedTurn(value)

States/Events
- MaxAltitudeChanged(current, min, max)
- MaxDistanceChanged(current, min, max)
- NoFlyOverMaxDistanceChanged(shouldNotFlyOver)


Ardrone3.SpeedSettings (limits)
--------------------------------

Commands
- MaxVerticalSpeed(current)
- MaxRotationSpeed(current)
- HullProtection(present)
- Outdoor(outdoor)

States/Events
- MaxVerticalSpeedChanged(current, min, max)
- MaxRotationSpeedChanged(current, min, max)


Piloting Style
--------------

Commands
- set_style(style)

States/Events
- style(style)


Obstacle Avoidance / Stereo Vision (if available)
-------------------------------------------------

Commands
- set_mode(mode)

States/Events
- state(mode)
- alert(error)


PreciseHome
-----------

Commands
- set_mode(mode)

States/Events
- state(mode)
- capabilities(available)


FollowMe (if available)
-----------------------

Commands
- start(mode)
- stop()
- configure(behavior, distance, elevation, azimuth)

States/Events
- state(mode)
- target_tracking_state(state)


Hand Land
---------

Commands
- enter()

States/Events
- state(state)


Wifi / Network (operational control)
------------------------------------

Commands
- set_ap_channel(band, channel)
- set_country(country)
- set_environment(indoor_outdoor)

States/Events
- country_changed(country)
- environment_changed(environment)


Mission (AirSDK)
----------------

Commands
- load(uid)
- start(uid)
- stop(uid)
- unload(uid)

States/Events
- state(uid, state)


Usage patterns (eDSL)
---------------------

- Invoke commands: `drone(Command(...))`
- Chain expectations: `.wait(timeout=...)`, `.success()`, `.failure()`
- Read states: `drone.get_state(StateMessage)`
- Compose: `all_of(...)`, `any_of(...)`, `check(lambda ...)`, `until(...)`


References
----------

- Olympe documentation (overview, eDSL, messages): https://developer.parrot.com/docs/olympe/index.html


