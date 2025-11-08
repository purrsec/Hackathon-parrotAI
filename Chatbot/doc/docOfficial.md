Ardrone3.Piloting and SpeedSettings
command message olympe.messages.ardrone3.Piloting.CancelMoveBy(_timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.CancelMoveBy

Cancel the current relative move. If there is no current relative move, this command has no effect.

Parameters:
_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.Piloting.CancelMoveBy

Result: Event moveByChanged() is triggered with state canceled.

command message olympe.messages.ardrone3.Piloting.CancelMoveTo(_timeout=5, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.CancelMoveTo

Cancel the current moveTo. If there is no current moveTo, this command has no effect.

Parameters:
_timeout (int) – command message timeout (defaults to 5)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.Piloting.CancelMoveTo

Result: Event moveToChanged() is triggered with state canceled.

Expectations: moveToChanged(status='CANCELED', _policy='wait')

command message olympe.messages.ardrone3.Piloting.Circle(direction, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.Circle

Make the fixed wing circle. The circle will use the CirclingAltitudeChanged() and the CirclingRadiusChanged()

Parameters:
direction (olympe.enums.ardrone3.Piloting.Circle_Direction) –

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.Piloting.Circle

Result: The fixed wing will circle in the given direction. Then, event FlyingStateChanged() is triggered with state set at hovering.

Expectations: FlyingStateChanged(state='hovering', _policy='wait')

command message olympe.messages.ardrone3.Piloting.Emergency(_timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.Emergency

Cut out the motors. This cuts immediatly the motors. The drone will fall. This command is sent on a dedicated high priority buffer which will infinitely retry to send it if the command is not delivered.

Parameters:
_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The drone immediatly cuts off its motors. Then, event FlyingStateChanged() is triggered.

Expectations: FlyingStateChanged(state='emergency', _policy='wait')

command message olympe.messages.ardrone3.Piloting.Landing(_timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.Landing

Land. Please note that on copters, if you put some positive gaz (in the PCMD()) during the landing, it will cancel it.

Parameters:
_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: On the copters, the drone lands if its FlyingStateChanged() was taking off, hovering or flying. On the fixed wings, the drone lands if its FlyingStateChanged() was hovering or flying. Then, event FlyingStateChanged() is triggered.

Expectations: FlyingStateChanged(state='landing', _policy='wait')

command message olympe.messages.ardrone3.Piloting.NavigateHome(start, _timeout=7, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.NavigateHome

Return home. Ask the drone to fly to its HomeChanged(). The availability of the return home can be get from NavigateHomeStateChanged(). Please note that the drone will wait to be hovering to start its return home. This means that it will wait to have a PCMD() set at 0.

Parameters:
start (u8) – 1 to start the navigate home, 0 to stop it

_timeout (int) – command message timeout (defaults to 7)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The drone will fly back to its home position. Then, event NavigateHomeStateChanged() is triggered. You can get a state pending if the drone is not ready to start its return home process but will do it as soon as it is possible.

Expectations: (NavigateHomeStateChanged(state='inProgress', reason='userRequest', _policy='wait') | NavigateHomeStateChanged(state='pending', reason='userRequest', _policy='wait') | NavigateHomeStateChanged(state='available', reason='stopped', _policy='wait'))

command message olympe.messages.ardrone3.Piloting.PCMD(flag, roll, pitch, yaw, gaz, timestampAndSeqNum, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.PCMD

Move the drone. The libARController is sending the command each 50ms. Please note that you should call setPilotingPCMD and not sendPilotingPCMD because the libARController is handling the periodicity and the buffer on which it is sent.

Parameters:
flag (u8) – Boolean flag: 1 if the roll and pitch values should be taken in consideration. 0 otherwise

roll (i8) – Roll angle as signed percentage. On copters: Roll angle expressed as signed percentage of the max pitch/roll setting, in range [-100, 100] -100 corresponds to a roll angle of max pitch/roll to the left (drone will fly left) 100 corresponds to a roll angle of max pitch/roll to the right (drone will fly right) This value may be clamped if necessary, in order to respect the maximum supported physical tilt of the copter. On fixed wings: Roll angle expressed as signed percentage of the physical max roll of the wing, in range [-100, 100] Negative value makes the plane fly to the left Positive value makes the plane fly to the right

pitch (i8) – Pitch angle as signed percentage. On copters: Expressed as signed percentage of the max pitch/roll setting, in range [-100, 100] -100 corresponds to a pitch angle of max pitch/roll towards sky (drone will fly backward) 100 corresponds to a pitch angle of max pitch/roll towards ground (drone will fly forward) This value may be clamped if necessary, in order to respect the maximum supported physical tilt of the copter. On fixed wings: Expressed as signed percentage of the physical max pitch of the wing, in range [-100, 100] Negative value makes the plane fly in direction of the sky Positive value makes the plane fly in direction of the ground

yaw (i8) – Yaw rotation speed as signed percentage. On copters: Expressed as signed percentage of the max yaw rotation speed setting, in range [-100, 100]. -100 corresponds to a counter-clockwise rotation of max yaw rotation speed 100 corresponds to a clockwise rotation of max yaw rotation speed This value may be clamped if necessary, in order to respect the maximum supported physical tilt of the copter. On fixed wings: Giving more than a fixed value (75% for the moment) triggers a circle. Positive value will trigger a clockwise circling Negative value will trigger a counter-clockwise circling

gaz (i8) – Throttle as signed percentage. On copters: Expressed as signed percentage of the max vertical speed setting, in range [-100, 100] -100 corresponds to a max vertical speed towards ground 100 corresponds to a max vertical speed towards sky This value may be clamped if necessary, in order to respect the maximum supported physical tilt of the copter. During the landing phase, putting some positive gaz will cancel the land. On fixed wings: Expressed as signed percentage of the physical max throttle, in range [-100, 100] Negative value makes the plane fly slower Positive value makes the plane fly faster

timestampAndSeqNum (u32) – Command timestamp in milliseconds (low 24 bits) + command sequence number (high 8 bits) [0;255].

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The drone moves! Yaaaaay! Event SpeedChanged(), AttitudeChanged() and GpsLocationChanged() (only if gps of the drone has fixed) are triggered.

command message olympe.messages.ardrone3.Piloting.SmartTakeOffLand(_timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.SmartTakeOffLand

Ask the drone to take off or land.

Parameters:
_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI Ai:
with an up to date firmware

Result: The drone takes off if its FlyingStateChanged() was landed. The drone lands if its FlyingStateChanged() was taking off, hovering or flying. Then, event FlyingStateChanged() is triggered.

Expectations: (FlyingStateChanged(state='takingoff', _policy='wait') | FlyingStateChanged(state='landing', _policy='wait'))

command message olympe.messages.ardrone3.Piloting.StartPilotedPOI(latitude, longitude, altitude, _timeout=5, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.StartPilotedPOI

Start a piloted Point Of Interest. During a piloted POI, the drone will always look at the given POI but can be piloted normally. However, yaw value is ignored. Camera tilt and pan command is also ignored. Ignored if PilotedPOI() state is UNAVAILABLE.

Parameters:
latitude (double) – Latitude of the location (in degrees) to look at

longitude (double) – Longitude of the location (in degrees) to look at

altitude (double) – Altitude above take off point (in m) to look at

_timeout (int) – command message timeout (defaults to 5)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.Piloting.StartPilotedPOI

Deprecated message

Warning

This message is deprecated and should no longer be used

Result: If the drone is hovering, event PilotedPOI() is triggered with state RUNNING. If the drone is not hovering, event PilotedPOI() is triggered with state PENDING, waiting to hover. When the drone hovers, the state will change to RUNNING. If the drone does not hover for a given time, piloted POI is canceled by the drone and state will change to AVAILABLE. Then, the drone will look at the given location.

Expectations: (PilotedPOI(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude, status='RUNNING', _policy='wait') | PilotedPOI(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude, status='PENDING', _policy='wait'))

command message olympe.messages.ardrone3.Piloting.StartPilotedPOIV2(latitude, longitude, altitude, mode, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.StartPilotedPOIV2

Start a piloted Point Of Interest. During a piloted POI, the drone always points towards the given POI but can be piloted normally. However, yaw value is ignored. The gimbal behavior depends on the mode argument: - in locked gimbal mode, the gimbal always looks at the POI, and gimbal control command is ignored by the drone, - in free gimbal mode, the gimbal initially looks at the POI, and is then freely controllable by the gimbal command. Ignored if PilotedPOIV2() state is UNAVAILABLE.

Parameters:
latitude (double) – Latitude of the location (in degrees) to look at

longitude (double) – Longitude of the location (in degrees) to look at

altitude (double) – Altitude above take off point (in m) to look at

mode (olympe.enums.ardrone3.Piloting.StartPilotedPOIV2_Mode) –

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: If the drone is hovering, event PilotedPOIV2() is triggered with state RUNNING. If the drone is not hovering, event PilotedPOIV2() is triggered with state PENDING, waiting to hover. When the drone hovers, the state changes to RUNNING. If the drone does not hover for a given time, piloted POI is canceled by the drone and state changes to AVAILABLE. Then, the drone looks at the given location.

Expectations: (PilotedPOIV2(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude, mode=self.mode, status='RUNNING', _policy='wait') | PilotedPOIV2(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude, mode=self.mode, status='PENDING', _policy='wait'))

command message olympe.messages.ardrone3.Piloting.StopPilotedPOI(_timeout=5, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.StopPilotedPOI

Stop the piloted Point Of Interest (with or without gimbal control). If PilotedPOI() or PilotedPOIV2() state is RUNNING or PENDING, stop it.

Parameters:
_timeout (int) – command message timeout (defaults to 5)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: Event PilotedPOI() or PilotedPOIV2() is triggered with state AVAILABLE.

Expectations: (PilotedPOI(status='AVAILABLE', _policy='wait') | PilotedPOIV2(status='AVAILABLE', _policy='wait'))

command message olympe.messages.ardrone3.Piloting.TakeOff(_timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.TakeOff

Ask the drone to take off. On the fixed wings (such as Disco): not used except to cancel a land.

Parameters:
_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: On the quadcopters: the drone takes off if its FlyingStateChanged() was landed. On the fixed wings, the landing process is aborted if the FlyingStateChanged() was landing. Then, event FlyingStateChanged() is triggered.

Expectations: FlyingStateChanged(state='takingoff', _policy='wait')

command message olympe.messages.ardrone3.Piloting.UserTakeOff(state, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.UserTakeOff

Prepare the drone to take off. On copters: initiates the thrown takeoff. Note that the drone will do the thrown take off even if it is steady. On fixed wings: initiates the take off process on the fixed wings. Setting the state to 0 will cancel the preparation. You can cancel it before that the drone takes off.

Parameters:
state (u8) – State of user take off mode - 1 to enter in user take off. - 0 to exit from user take off.

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The drone will arm its motors if not already armed. Then, event FlyingStateChanged() is triggered with state set at motor ramping. Then, event FlyingStateChanged() is triggered with state set at userTakeOff. Then user can throw the drone to make it take off.

Expectations: FlyingStateChanged(_policy='wait')

command message olympe.messages.ardrone3.Piloting.moveBy(dX, dY, dZ, dPsi, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.moveBy

Move the drone to a relative position and rotate heading by a given angle. Moves are relative to the current drone orientation, (drone’s reference). Also note that the given rotation will not modify the move (i.e. moves are always rectilinear).

Parameters:
dX (float) – Wanted displacement along the front axis [m]

dY (float) – Wanted displacement along the right axis [m]

dZ (float) – Wanted displacement along the down axis [m]

dPsi (float) – Wanted rotation of heading [rad]

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The drone will move of the given offsets. Then, event moveByEnd() is triggered. If you send a second relative move command, the drone will trigger a moveByEnd() with the offsets it managed to do before this new command and the value of error set to interrupted.

Expectations: moveByEnd(_policy='wait')

command message olympe.messages.ardrone3.Piloting.moveTo(latitude, longitude, altitude, orientation_mode, heading, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.Piloting.moveTo

Move the drone to a specified location. If a new command moveTo is sent, the drone will immediatly run it (no cancel will be issued). If a CancelMoveTo() command is sent, the moveTo is stopped. During the moveTo, all pitch, roll and gaz values of the piloting command will be ignored by the drone. However, the yaw value can be used.

Parameters:
latitude (double) – Latitude of the location (in degrees) to reach

longitude (double) – Longitude of the location (in degrees) to reach

altitude (double) – Altitude above take off point (in m) to reach

orientation_mode (olympe.enums.ardrone3.Piloting.MoveTo_Orientation_mode) –

heading (float) – Heading (relative to the North in degrees). This value is only used if the orientation mode is HEADING_START or HEADING_DURING

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: Event moveToChanged() is triggered with state running. Then, the drone will move to the given location. Then, event moveToChanged() is triggered with state succeed.

Expectations: moveToChanged(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude, orientation_mode=self.orientation_mode, status='RUNNING', _policy='wait')

enum olympe.enums.ardrone3.Piloting.Circle_Direction
The circling direction

CW:
Circling ClockWise (0)

CCW:
Circling Counter ClockWise (1)

default:
Use drone default Circling direction set by CirclingDirection cmd (2)

enum olympe.enums.ardrone3.Piloting.MoveTo_Orientation_mode
Orientation mode of the move to

Enum aliases:

olympe.enums.ardrone3.MoveTo_Orientation_mode

olympe.enums.ardrone3.MoveToChanged_Orientation_mode

olympe.enums.move.orientation_mode

NONE:
The drone won’t change its orientation (0)

TO_TARGET:
The drone will make a rotation to look in direction of the given location (1)

HEADING_START:
The drone will orientate itself to the given heading before moving to the location (2)

HEADING_DURING:
The drone will orientate itself to the given heading while moving to the location (3)

enum olympe.enums.ardrone3.Piloting.StartPilotedPOIV2_Mode
POI mode

Enum aliases:

olympe.enums.ardrone3.StartPilotedPOIV2_Mode

olympe.enums.ardrone3.PilotedPOIV2_Mode

locked_gimbal:
Gimbal is locked on the POI (0)

locked_once_gimbal:
Gimbal is locked on the POI once, then it is freely controllable (1)

free_gimbal:
Gimbal is freely controllable (2)

event message olympe.messages.ardrone3.PilotingState.AirSpeedChanged(airSpeed=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.AirSpeedChanged

Drone’s air speed changed Expressed in the drone’s referential.

Parameters:
airSpeed (float) – Speed relative to air on x axis (speed is always > 0) (in m/s)

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingState.AirSpeedChanged

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.AlertStateChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.AlertStateChanged

Alert state.

Parameters:
state (olympe.enums.ardrone3.PilotingState.AlertStateChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Deprecated message

Warning

This message is deprecated and should no longer be used

Triggered when an alert happens on the drone.

event message olympe.messages.ardrone3.PilotingState.AltitudeAboveGroundChanged(altitude=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.AltitudeAboveGroundChanged

Drone’s altitude above ground changed.

Parameters:
altitude (float) – Altitude in meters

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.AltitudeChanged(altitude=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.AltitudeChanged

Drone’s altitude changed. The altitude reported is the altitude above the take off point. To get the altitude above sea level, see GpsLocationChanged().

Parameters:
altitude (double) – Altitude in meters

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.AttitudeChanged(roll=None, pitch=None, yaw=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.AttitudeChanged

Drone’s attitude changed.

Parameters:
roll (float) – roll value (in radian)

pitch (float) – Pitch value (in radian)

yaw (float) – Yaw value (in radian)

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.FlyingStateChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.FlyingStateChanged

Flying state.

Parameters:
state (olympe.enums.ardrone3.PilotingState.FlyingStateChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered when the flying state changes.

event message olympe.messages.ardrone3.PilotingState.ForcedLandingAutoTrigger(reason=None, delay=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.ForcedLandingAutoTrigger

Forced landing auto trigger information.

Parameters:
reason (olympe.enums.ardrone3.PilotingState.ForcedLandingAutoTrigger_Reason) –

delay (u32) – Delay until the landing is automatically triggered by the drone, in seconds. If reason is none this information has no meaning.

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingState.ForcedLandingAutoTrigger

Triggered at connection, and when forced landing auto trigger information changes, then every seconds while reason is different from none.

event message olympe.messages.ardrone3.PilotingState.GpsLocationChanged(latitude=None, longitude=None, altitude=None, latitude_accuracy=None, longitude_accuracy=None, altitude_accuracy=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.GpsLocationChanged

Drone’s location changed.

Parameters:
latitude (double) – Latitude location in decimal degrees (500.0 if not available)

longitude (double) – Longitude location in decimal degrees (500.0 if not available)

altitude (double) – Altitude location in meters.

latitude_accuracy (i8) – Latitude location error in meters (1 sigma/standard deviation) -1 if not available.

longitude_accuracy (i8) – Longitude location error in meters (1 sigma/standard deviation) -1 if not available.

altitude_accuracy (i8) – Altitude location error in meters (1 sigma/standard deviation) -1 if not available.

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.HeadingLockedStateChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.HeadingLockedStateChanged

Drone’s heading locked state.

Parameters:
state (olympe.enums.ardrone3.PilotingState.HeadingLockedStateChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

event message olympe.messages.ardrone3.PilotingState.HoveringWarning(no_gps_too_dark=None, no_gps_too_high=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.HoveringWarning

Indicate that the drone may have difficulties to maintain a fix position when hovering.

Parameters:
no_gps_too_dark (u8) – 1 if the drone doesn’t have a GPS fix and there is not enough light.

no_gps_too_high (u8) – 1 if the drone doesn’t have a GPS fix and is flying too high.

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered at connection and on changes.

event message olympe.messages.ardrone3.PilotingState.IcingLevelChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.IcingLevelChanged

Propeller icing level. Informs that drone propellers are iced, which result in a degraded flying behavior.

Parameters:
state (olympe.enums.ardrone3.PilotingState.IcingLevelChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI Ai:
with an up to date firmware

Triggered at connection and on changes.

event message olympe.messages.ardrone3.PilotingState.LandingStateChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.LandingStateChanged

Landing state. Only available for fixed wings (which have two landing modes).

Parameters:
state (olympe.enums.ardrone3.PilotingState.LandingStateChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingState.LandingStateChanged

Triggered when the landing state changes.

event message olympe.messages.ardrone3.PilotingState.MotionState(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.MotionState

Motion state. If MotionDetection() is disabled, motion is steady. This information is only valid when the drone is not flying.

Parameters:
state (olympe.enums.ardrone3.PilotingState.MotionState_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered when the FlyingStateChanged() is landed and the MotionDetection() is enabled and the motion state changes. This event is triggered at a filtered rate.

event message olympe.messages.ardrone3.PilotingState.NavigateHomeStateChanged(state=None, reason=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.NavigateHomeStateChanged

Return home state. Availability is related to gps fix, magnetometer calibration.

Parameters:
state (olympe.enums.ardrone3.PilotingState.NavigateHomeStateChanged_State) –

reason (olympe.enums.ardrone3.PilotingState.NavigateHomeStateChanged_Reason) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Deprecated message

Warning

This message is deprecated and should no longer be used

Triggered by NavigateHome() or when the state of the return home changes.

event message olympe.messages.ardrone3.PilotingState.PilotedPOI(latitude=None, longitude=None, altitude=None, status=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.PilotedPOI

Piloted POI state.

Parameters:
latitude (double) – Latitude of the location (in degrees) to look at. This information is only valid when the state is pending or running.

longitude (double) – Longitude of the location (in degrees) to look at. This information is only valid when the state is pending or running.

altitude (double) – Altitude above take off point (in m) to look at. This information is only valid when the state is pending or running.

status (olympe.enums.ardrone3.PilotingState.PilotedPOI_Status) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingState.PilotedPOI

Deprecated message

Warning

This message is deprecated and should no longer be used

Triggered by StartPilotedPOI() or StopPilotedPOI() or when piloted POI becomes unavailable.

event message olympe.messages.ardrone3.PilotingState.PilotedPOIV2(latitude=None, longitude=None, altitude=None, mode=None, status=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.PilotedPOIV2

Piloted POI state.

Parameters:
latitude (double) – Latitude of the location (in degrees) to look at. This information is only valid when the state is pending or running.

longitude (double) – Longitude of the location (in degrees) to look at. This information is only valid when the state is pending or running.

altitude (double) – Altitude above take off point (in m) to look at. This information is only valid when the state is pending or running.

mode (olympe.enums.ardrone3.PilotingState.PilotedPOIV2_Mode) –

status (olympe.enums.ardrone3.PilotingState.PilotedPOIV2_Status) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by StartPilotedPOIV2() or StopPilotedPOI() or when piloted POI becomes available or unavailable.

event message olympe.messages.ardrone3.PilotingState.PositionChanged(latitude=None, longitude=None, altitude=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.PositionChanged

Drone’s position changed.

Parameters:
latitude (double) – Latitude position in decimal degrees (500.0 if not available)

longitude (double) – Longitude position in decimal degrees (500.0 if not available)

altitude (double) – Altitude in meters (from GPS)

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Deprecated message

Warning

This message is deprecated and should no longer be used

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.ReturnHomeBatteryCapacity(status=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.ReturnHomeBatteryCapacity

Battery capacity status to return home.

Parameters:
status (olympe.enums.ardrone3.PilotingState.ReturnHomeBatteryCapacity_Status) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingState.ReturnHomeBatteryCapacity

Triggered when the status of the battery capacity to do a return home changes. This means that it is triggered either when the battery level changes, when the distance to the home changes or when the position of the home changes.

event message olympe.messages.ardrone3.PilotingState.SpeedChanged(speedX=None, speedY=None, speedZ=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.SpeedChanged

Drone’s speed changed. Expressed in the NED referential (North-East- Down).

Parameters:
speedX (float) – Speed relative to the North (when drone moves to the north, speed is > 0) (in m/s)

speedY (float) – Speed relative to the East (when drone moves to the east, speed is > 0) (in m/s)

speedZ (float) – Speed on the z axis (when drone moves down, speed is > 0) (in m/s)

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered regularly.

event message olympe.messages.ardrone3.PilotingState.VibrationLevelChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.VibrationLevelChanged

Vibration level.

Parameters:
state (olympe.enums.ardrone3.PilotingState.VibrationLevelChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered at connection and on changes.

event message olympe.messages.ardrone3.PilotingState.WindStateChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.WindStateChanged

Wind state.

Parameters:
state (olympe.enums.ardrone3.PilotingState.WindStateChanged_State) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered at connection and on changes.

event message olympe.messages.ardrone3.PilotingState.moveByChanged(dXAsked=None, dYAsked=None, dZAsked=None, dPsiAsked=None, dX=None, dY=None, dZ=None, dPsi=None, status=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.moveByChanged

Relative move changed.

Parameters:
dXAsked (float) – Distance asked to be traveled along the front axis [m]

dYAsked (float) – Distance asked to be traveled along the right axis [m]

dZAsked (float) – Distance asked to be traveled along the down axis [m]

dPsiAsked (float) – Relative angle asked to be applied on heading [rad]

dX (float) – Actual distance traveled along the front axis [m]. This information is only valid when the state is DONE or CANCELED.

dY (float) – Actual distance traveled along the right axis [m]. This information is only valid when the state is DONE or CANCELED.

dZ (float) – Actual distance traveled along the down axis [m]. This information is only valid when the state is DONE or CANCELED.

dPsi (float) – Actual applied angle on heading [rad]. This information is only valid when the state is DONE or CANCELED.

status (olympe.enums.ardrone3.PilotingState.MoveByChanged_Status) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingState.moveByChanged

Triggered by moveBy(), or CancelMoveBy() or when the drone’s relative move state changes.

event message olympe.messages.ardrone3.PilotingState.moveToChanged(latitude=None, longitude=None, altitude=None, orientation_mode=None, heading=None, status=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingState.moveToChanged

The drone moves or moved to a given location.

Parameters:
latitude (double) – Latitude of the location (in degrees) to reach

longitude (double) – Longitude of the location (in degrees) to reach

altitude (double) – Altitude above take off point (in m) to reach

orientation_mode (olympe.enums.ardrone3.PilotingState.MoveToChanged_Orientation_mode) –

heading (float) – Heading (relative to the North in degrees). This value is only used if the orientation mode is HEADING_START or HEADING_DURING

status (olympe.enums.ardrone3.PilotingState.MoveToChanged_Status) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by moveTo() or when the drone did reach the given position.

enum olympe.enums.ardrone3.PilotingState.AlertStateChanged_State
Drone alert state

none:
No alert (0)

user:
User emergency alert (1)

cut_out:
Cut out alert (2)

critical_battery:
Critical battery alert (3)

low_battery:
Low battery alert (4)

too_much_angle:
The angle of the drone is too high (5)

almost_empty_battery:
Almost empty battery alert (6)

magneto_pertubation:
Magnetometer is disturbed by a magnetic element (7)

magneto_low_earth_field:
Local terrestrial magnetic field is too weak (8)

enum olympe.enums.ardrone3.PilotingState.FlyingStateChanged_State
Drone flying state

landed:
Landed state (0)

takingoff:
Taking off state (1)

hovering:
Hovering / Circling (for fixed wings) state (2)

flying:
Flying state (3)

landing:
Landing state (4)

emergency:
Emergency state (5)

usertakeoff:
User take off state. Waiting for user action to take off. (6)

motor_ramping:
Motor ramping state. (7)

emergency_landing:
Emergency landing state. Drone autopilot has detected defective sensor(s). Only Yaw argument in PCMD is taken into account. All others flying commands are ignored. (8)

enum olympe.enums.ardrone3.PilotingState.ForcedLandingAutoTrigger_Reason
Reason of the forced landing.

NONE:
There is no forced landing auto trigger planned. (0)

BATTERY_CRITICAL_SOON:
Battery will soon be critical, so forced landing auto trigger is planned. (1)

PROPELLER_ICING_CRITICAL:
Propellers are critically iced, so forced landing auto trigger is planned. (2)

BATTERY_TOO_COLD:
Battery is too cold, so forced landing auto trigger is planned. (3)

BATTERY_TOO_HOT:
Battery is too hot, so forced landing auto trigger is planned. (4)

ESC_TOO_HOT:
ESC (motor) is too hot, so forced landing auto trigger is planned. (5)

enum olympe.enums.ardrone3.PilotingState.HeadingLockedStateChanged_State
Magneto state

Enum aliases:

olympe.enums.ardrone3.WindStateChanged_State

olympe.enums.ardrone3.VibrationLevelChanged_State

olympe.enums.ardrone3.HeadingLockedStateChanged_State

olympe.enums.ardrone3.IcingLevelChanged_State

ok:
Magnetometer state allows heading lock (0)

warning:
Magnetometer detects a weak magnetic field (close to Earth pole), or a pertubated local magnetic field. Magnetometer has not lost heading lock yet. (1)

critical:
Magnetometer lost heading lock. (2)

enum olympe.enums.ardrone3.PilotingState.IcingLevelChanged_State
Drone propeller icing level

Enum aliases:

olympe.enums.ardrone3.WindStateChanged_State

olympe.enums.ardrone3.VibrationLevelChanged_State

olympe.enums.ardrone3.HeadingLockedStateChanged_State

olympe.enums.ardrone3.IcingLevelChanged_State

ok:
The level of propeller icing is low or non-existent. (0)

warning:
The level of propeller icing begins to be too strong and can impact drone flying capacity. (1)

critical:
The level of propeller icing is high, will impact drone flying capacity and eventually damage motors. (2)

enum olympe.enums.ardrone3.PilotingState.LandingStateChanged_State
Drone landing state

linear:
Linear landing (0)

spiral:
Spiral landing (1)

enum olympe.enums.ardrone3.PilotingState.MotionState_State
Motion state

steady:
Drone is steady (0)

moving:
Drone is moving (1)

enum olympe.enums.ardrone3.PilotingState.MoveByChanged_Status
Status of the relative move

Enum aliases:

olympe.enums.ardrone3.MoveToChanged_Status

olympe.enums.ardrone3.MoveByChanged_Status

RUNNING:
The drone is actually flying to the relative position (0)

DONE:
The drone has reached the target (1)

CANCELED:
The relative move has been canceled, either by a CancelMoveBy command or when a disconnection appears. (2)

ERROR:
The relative move has not been finished or started because of an error. (3)

enum olympe.enums.ardrone3.PilotingState.MoveToChanged_Orientation_mode
Orientation mode of the move to

Enum aliases:

olympe.enums.ardrone3.MoveTo_Orientation_mode

olympe.enums.ardrone3.MoveToChanged_Orientation_mode

olympe.enums.move.orientation_mode

NONE:
The drone won’t change its orientation (0)

TO_TARGET:
The drone will make a rotation to look in direction of the given location (1)

HEADING_START:
The drone will orientate itself to the given heading before moving to the location (2)

HEADING_DURING:
The drone will orientate itself to the given heading while moving to the location (3)

enum olympe.enums.ardrone3.PilotingState.MoveToChanged_Status
Status of the move to

Enum aliases:

olympe.enums.ardrone3.MoveToChanged_Status

olympe.enums.ardrone3.MoveByChanged_Status

RUNNING:
The drone is actually flying to the given position (0)

DONE:
The drone has reached the target (1)

CANCELED:
The move to has been canceled, either by a CancelMoveTo command or when a disconnection appears. (2)

ERROR:
The move to has not been finished or started because of an error. (3)

enum olympe.enums.ardrone3.PilotingState.NavigateHomeStateChanged_Reason
Reason of the state

userRequest:
User requested a navigate home (available->inProgress) (0)

connectionLost:
Connection between controller and product lost (available->inProgress) (1)

lowBattery:
Low battery occurred (available->inProgress) (2)

finished:
Navigate home is finished (inProgress->available) (3)

stopped:
Navigate home has been stopped (inProgress->available) (4)

disabled:
Navigate home disabled by product (inProgress->unavailable or available->unavailable) (5)

enabled:
Navigate home enabled by product (unavailable->available) (6)

flightplan:
Return to home during a flightplan (available->in_progress) (7)

icing:
Return to home triggered by propeller icing event (available->in_progress) (8)

enum olympe.enums.ardrone3.PilotingState.NavigateHomeStateChanged_State
State of navigate home

Enum aliases:

olympe.enums.ardrone3.NavigateHomeStateChanged_State

olympe.enums.rth.state

available:
Navigate home is available (0)

inProgress:
Navigate home is in progress (1)

unavailable:
Navigate home is not available (2)

pending:
Navigate home has been received, but its process is pending (3)

enum olympe.enums.ardrone3.PilotingState.PilotedPOIV2_Mode
POI mode. This information is only valid when the state is pending or running.

Enum aliases:

olympe.enums.ardrone3.StartPilotedPOIV2_Mode

olympe.enums.ardrone3.PilotedPOIV2_Mode

locked_gimbal:
Gimbal is locked on the POI (0)

locked_once_gimbal:
Gimbal is locked on the POI once, then it is freely controllable (1)

free_gimbal:
Gimbal is freely controllable (2)

enum olympe.enums.ardrone3.PilotingState.PilotedPOIV2_Status
Status of the Piloted POI

Enum aliases:

olympe.enums.ardrone3.PilotedPOI_Status

olympe.enums.ardrone3.PilotedPOIV2_Status

UNAVAILABLE:
The piloted POI is not available (0)

AVAILABLE:
The piloted POI is available (1)

PENDING:
Piloted POI has been requested. Waiting to be in state that allows the piloted POI to start (2)

RUNNING:
Piloted POI is running (3)

enum olympe.enums.ardrone3.PilotingState.PilotedPOI_Status
Status of the Piloted POI

Enum aliases:

olympe.enums.ardrone3.PilotedPOI_Status

olympe.enums.ardrone3.PilotedPOIV2_Status

UNAVAILABLE:
The piloted POI is not available (0)

AVAILABLE:
The piloted POI is available (1)

PENDING:
Piloted POI has been requested. Waiting to be in state that allow the piloted POI to start (2)

RUNNING:
Piloted POI is running (3)

enum olympe.enums.ardrone3.PilotingState.ReturnHomeBatteryCapacity_Status
Status of battery to return home

OK:
The battery is full enough to do a return home (0)

WARNING:
The battery is about to be too discharged to do a return home (1)

CRITICAL:
The battery level is too low to return to the home position (2)

UNKNOWN:
Battery capacity to do a return home is unknown. This can be either because the home is unknown or the position of the drone is unknown, or the drone has not enough information to determine how long it takes to fly home. (3)

enum olympe.enums.ardrone3.PilotingState.VibrationLevelChanged_State
Drone vibration level

Enum aliases:

olympe.enums.ardrone3.WindStateChanged_State

olympe.enums.ardrone3.VibrationLevelChanged_State

olympe.enums.ardrone3.HeadingLockedStateChanged_State

olympe.enums.ardrone3.IcingLevelChanged_State

ok:
The level of vibration can be handled properly by the drone. (0)

warning:
The level of vibration begins to be too strong for the drone to fly correctly. (1)

critical:
The level of vibration is too strong for the drone to fly correctly. (2)

enum olympe.enums.ardrone3.PilotingState.WindStateChanged_State
Drone wind state

Enum aliases:

olympe.enums.ardrone3.WindStateChanged_State

olympe.enums.ardrone3.VibrationLevelChanged_State

olympe.enums.ardrone3.HeadingLockedStateChanged_State

olympe.enums.ardrone3.IcingLevelChanged_State

ok:
The wind strength can be handled properly by the drone. (0)

warning:
The wind strength begins to be too strong for the drone to fly correctly. (1)

critical:
The wind strength is too strong for the drone to fly correctly. (2)

event message olympe.messages.ardrone3.PilotingEvent.UserTakeoffReady(_policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingEvent.UserTakeoffReady

Sent when the drone is ready to be thrown during a user takeoff.

Parameters:
_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI Ai:
with an up to date firmware

Triggered when the motors are done ramping up during a [user takeoff](UserTakeOff()).

event message olympe.messages.ardrone3.PilotingEvent.moveByEnd(dX=None, dY=None, dZ=None, dPsi=None, error=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingEvent.moveByEnd

Relative move ended. Informs about the move that the drone managed to do and why it stopped.

Parameters:
dX (float) – Distance traveled along the front axis [m]

dY (float) – Distance traveled along the right axis [m]

dZ (float) – Distance traveled along the down axis [m]

dPsi (float) – Applied angle on heading [rad]

error (olympe.enums.ardrone3.PilotingEvent.MoveByEnd_Error) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered when the drone reaches its target or when it is interrupted by another [moveBy command](moveBy()) or when an error occurs.

enum olympe.enums.ardrone3.PilotingEvent.MoveByEnd_Error
Error to explain the event

ok:
No Error ; The relative displacement (0)

unknown:
Unknown generic error (1)

busy:
The Device is busy ; command moveBy ignored (2)

notAvailable:
Command moveBy is not available ; command moveBy ignored (3)

interrupted:
Command moveBy interrupted (4)

command message olympe.messages.ardrone3.PilotingSettings.AbsolutControl(on, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.AbsolutControl

Set absolut control.

Parameters:
on (u8) – 1 to enable, 0 to disable

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.AbsolutControl

Deprecated message

Warning

This message is deprecated and should no longer be used

command message olympe.messages.ardrone3.PilotingSettings.BankedTurn(value, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.BankedTurn

Set banked turn mode. When banked turn mode is enabled, the drone will use yaw values from the piloting command to infer with roll and pitch on the drone when its horizontal speed is not null.

Parameters:
value (u8) – 1 to enable, 0 to disable

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The banked turn mode is enabled or disabled. Then, event BankedTurnChanged() is triggered.

Expectations: BankedTurnChanged(state=self.value, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.CirclingAltitude(value, _timeout=3, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.CirclingAltitude

Set min circling altitude (not used during take off). Only available for fixed wings.

Parameters:
value (u16) – The circling altitude in meter

_timeout (int) – command message timeout (defaults to 3)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.CirclingAltitude

Result: The circling altitude is set. Then, event CirclingAltitudeChanged() is triggered.

Expectations: CirclingAltitudeChanged(value=self.value, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.CirclingDirection(value, _timeout=3, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.CirclingDirection

Set default circling direction. This direction will be used when the drone use an automatic circling or when Circle() is sent with direction default. Only available for fixed wings.

Parameters:
value (olympe.enums.ardrone3.PilotingSettings.CirclingDirection_Value) –

_timeout (int) – command message timeout (defaults to 3)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.CirclingDirection

Result: The circling direction is set. Then, event CirclingDirectionChanged() is triggered.

Expectations: CirclingDirectionChanged(value=self.value, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.CirclingRadius(value, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.CirclingRadius

Set circling radius. Only available for fixed wings.

Parameters:
value (u16) – The circling radius in meter

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.CirclingRadius

Deprecated message

Warning

This message is deprecated and should no longer be used

Result: The circling radius is set. Then, event CirclingRadiusChanged() is triggered.

Expectations: CirclingRadiusChanged(value=self.value, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.MaxAltitude(current, _timeout=20, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.MaxAltitude

Set max altitude. The drone will not fly over this max altitude when it is in manual piloting. Please note that if you set a max altitude which is below the current drone altitude, the drone will not go to given max altitude. You can get the bounds in the event MaxAltitudeChanged().

Parameters:
current (float) – Current altitude max in m

_timeout (int) – command message timeout (defaults to 20)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The max altitude is set. Then, event MaxAltitudeChanged() is triggered.

Expectations: MaxAltitudeChanged(current=self.current, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.MaxDistance(value, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.MaxDistance

Set max distance. You can get the bounds from the event MaxDistanceChanged(). If NoFlyOverMaxDistanceChanged() is activated, the drone won’t fly over the given max distance.

Parameters:
value (float) – Current max distance in meter

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The max distance is set. Then, event MaxDistanceChanged() is triggered.

Expectations: MaxDistanceChanged(current=self.value, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.MaxTilt(current, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.MaxTilt

Set max pitch/roll. This represent the max inclination allowed by the drone. You can get the bounds with the commands MaxTiltChanged().

Parameters:
current (float) – Current tilt max in degree

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The max pitch/roll is set. Then, event MaxTiltChanged() is triggered.

Expectations: MaxTiltChanged(current=self.current, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.MinAltitude(current, _timeout=20, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.MinAltitude

Set minimum altitude. Only available for fixed wings.

Parameters:
current (float) – Current altitude min in m

_timeout (int) – command message timeout (defaults to 20)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.MinAltitude

Result: The minimum altitude is set. Then, event MinAltitudeChanged() is triggered.

Expectations: MinAltitudeChanged(current=self.current, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.NoFlyOverMaxDistance(shouldNotFlyOver, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.NoFlyOverMaxDistance

Enable geofence. If geofence is enabled, the drone won’t fly over the given max distance. You can get the max distance from the event MaxDistanceChanged(). For copters: the distance is computed from the controller position, if this position is not known, it will use the take off. For fixed wings: the distance is computed from the take off position.

Parameters:
shouldNotFlyOver (u8) – 1 if the drone can’t fly further than max distance, 0 if no limitation on the drone should be done

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: Geofencing is enabled or disabled. Then, event NoFlyOverMaxDistanceChanged() is triggered.

Expectations: NoFlyOverMaxDistanceChanged(shouldNotFlyOver=self.shouldNotFlyOver, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.PitchMode(value, _timeout=3, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.PitchMode

Set pitch mode. Only available for fixed wings.

Parameters:
value (olympe.enums.ardrone3.PilotingSettings.PitchMode_Value) –

_timeout (int) – command message timeout (defaults to 3)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.PitchMode

Result: The pitch mode is set. Then, event PitchModeChanged() is triggered.

Expectations: PitchModeChanged(value=self.value, _policy='wait')

command message olympe.messages.ardrone3.PilotingSettings.SetMotionDetectionMode(enable, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettings.SetMotionDetectionMode

Enable/disable the motion detection. If the motion detection is enabled, the drone will send its MotionState() when its FlyingStateChanged() is landed. If the motion detection is disabled, MotionState() is steady.

Parameters:
enable (u8) – 1 to enable the motion detection, 0 to disable it.

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettings.SetMotionDetectionMode

Result: The motion detection is enabled or disabled. Then, event MotionDetection() is triggered. After that, if enabled and FlyingStateChanged() is landed, the MotionState() is triggered upon changes.

Expectations: MotionState(state=self.enable, _policy='wait')

enum olympe.enums.ardrone3.PilotingSettings.CirclingDirection_Value
The circling direction

Enum aliases:

olympe.enums.ardrone3.CirclingDirection_Value

olympe.enums.ardrone3.CirclingDirectionChanged_Value

CW:
Circling ClockWise (0)

CCW:
Circling Counter ClockWise (1)

enum olympe.enums.ardrone3.PilotingSettings.PitchMode_Value
The Pitch mode

Enum aliases:

olympe.enums.ardrone3.PitchMode_Value

olympe.enums.ardrone3.PitchModeChanged_Value

NORMAL:
Positive pitch values will make the drone lower its nose. Negative pitch values will make the drone raise its nose. (0)

INVERTED:
Pitch commands are inverted. Positive pitch values will make the drone raise its nose. Negative pitch values will make the drone lower its nose. (1)

event message olympe.messages.ardrone3.PilotingSettingsState.AbsolutControlChanged(on=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.AbsolutControlChanged

Absolut control.

Parameters:
on (u8) – 1 if enabled, 0 if disabled

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettingsState.AbsolutControlChanged

Deprecated message

Warning

This message is deprecated and should no longer be used

event message olympe.messages.ardrone3.PilotingSettingsState.BankedTurnChanged(state=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.BankedTurnChanged

Banked Turn mode. If banked turn mode is enabled, the drone will use yaw values from the piloting command to infer with roll and pitch on the drone when its horizontal speed is not null.

Parameters:
state (u8) – 1 if enabled, 0 if disabled

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by BankedTurn().

event message olympe.messages.ardrone3.PilotingSettingsState.CirclingAltitudeChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.CirclingAltitudeChanged

Circling altitude. Bounds will be automatically adjusted according to the MaxAltitudeChanged(). Only sent by fixed wings.

Parameters:
current (u16) – The current circling altitude in meter

min (u16) – Range min of circling altitude in meter

max (u16) – Range max of circling altitude in meter

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettingsState.CirclingAltitudeChanged

Triggered by CirclingAltitude() or when bounds change due to MaxAltitude().

event message olympe.messages.ardrone3.PilotingSettingsState.CirclingDirectionChanged(value=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.CirclingDirectionChanged

Circling direction. Only sent by fixed wings.

Parameters:
value (olympe.enums.ardrone3.PilotingSettingsState.CirclingDirectionChanged_Value) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettingsState.CirclingDirectionChanged

Triggered by CirclingDirection().

event message olympe.messages.ardrone3.PilotingSettingsState.CirclingRadiusChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.CirclingRadiusChanged

Circling radius. Only sent by fixed wings.

Parameters:
current (u16) – The current circling radius in meter

min (u16) – Range min of circling radius in meter

max (u16) – Range max of circling radius in meter

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettingsState.CirclingRadiusChanged

Deprecated message

Warning

This message is deprecated and should no longer be used

Triggered by CirclingRadius().

event message olympe.messages.ardrone3.PilotingSettingsState.MaxAltitudeChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.MaxAltitudeChanged

Max altitude. The drone will not fly higher than this altitude (above take off point).

Parameters:
current (float) – Current altitude max

min (float) – Range min of altitude

max (float) – Range max of altitude

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by MaxAltitude().

event message olympe.messages.ardrone3.PilotingSettingsState.MaxDistanceChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.MaxDistanceChanged

Max distance.

Parameters:
current (float) – Current max distance in meter

min (float) – Minimal possible max distance

max (float) – Maximal possible max distance

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by MaxDistance().

event message olympe.messages.ardrone3.PilotingSettingsState.MaxTiltChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.MaxTiltChanged

Max pitch/roll. The drone will not fly higher than this altitude (above take off point).

Parameters:
current (float) – Current max tilt

min (float) – Range min of tilt

max (float) – Range max of tilt

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by MaxAltitude().

event message olympe.messages.ardrone3.PilotingSettingsState.MinAltitudeChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.MinAltitudeChanged

Min altitude. Only sent by fixed wings.

Parameters:
current (float) – Current altitude min

min (float) – Range min of altitude min

max (float) – Range max of altitude min

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettingsState.MinAltitudeChanged

Triggered by MinAltitude().

event message olympe.messages.ardrone3.PilotingSettingsState.MotionDetection(enabled=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.MotionDetection

State of the motion detection.

Parameters:
enabled (u8) – 1 if motion detection is enabled, 0 otherwise.

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by SetMotionDetectionMode()

event message olympe.messages.ardrone3.PilotingSettingsState.NoFlyOverMaxDistanceChanged(shouldNotFlyOver=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.NoFlyOverMaxDistanceChanged

Geofencing. If set, the drone won’t fly over the MaxDistanceChanged().

Parameters:
shouldNotFlyOver (u8) – 1 if the drone won’t fly further than max distance, 0 if no limitation on the drone will be done

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by NoFlyOverMaxDistance().

event message olympe.messages.ardrone3.PilotingSettingsState.PitchModeChanged(value=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.PilotingSettingsState.PitchModeChanged

Pitch mode.

Parameters:
value (olympe.enums.ardrone3.PilotingSettingsState.PitchModeChanged_Value) –

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.PilotingSettingsState.PitchModeChanged

Triggered by PitchMode().

enum olympe.enums.ardrone3.PilotingSettingsState.CirclingDirectionChanged_Value
The circling direction

Enum aliases:

olympe.enums.ardrone3.CirclingDirection_Value

olympe.enums.ardrone3.CirclingDirectionChanged_Value

CW:
Circling ClockWise (0)

CCW:
Circling Counter ClockWise (1)

enum olympe.enums.ardrone3.PilotingSettingsState.PitchModeChanged_Value
The Pitch mode

Enum aliases:

olympe.enums.ardrone3.PitchMode_Value

olympe.enums.ardrone3.PitchModeChanged_Value

NORMAL:
Positive pitch values will make the drone lower its nose. Negative pitch values will make the drone raise its nose. (0)

INVERTED:
Pitch commands are inverted. Positive pitch values will make the drone raise its nose. Negative pitch values will make the drone lower its nose. (1)

command message olympe.messages.ardrone3.SpeedSettings.HullProtection(present, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettings.HullProtection

Set the presence of hull protection.

Parameters:
present (u8) – 1 if present, 0 if not present

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.SpeedSettings.HullProtection

Result: The drone knows that it has a hull protection. Then, event HullProtectionChanged() is triggered.

Expectations: HullProtectionChanged(present=self.present, _policy='wait')

command message olympe.messages.ardrone3.SpeedSettings.MaxPitchRollRotationSpeed(current, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettings.MaxPitchRollRotationSpeed

Set max pitch/roll rotation speed.

Parameters:
current (float) – Current max pitch/roll rotation speed in degree/s

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The max pitch/roll rotation speed is set. Then, event MaxPitchRollRotationSpeedChanged() is triggered.

Expectations: MaxPitchRollRotationSpeedChanged(current=self.current, _policy='wait')

command message olympe.messages.ardrone3.SpeedSettings.MaxRotationSpeed(current, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettings.MaxRotationSpeed

Set max rotation speed.

Parameters:
current (float) – Current max yaw rotation speed in degree/s

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The max rotation speed is set. Then, event MaxRotationSpeedChanged() is triggered.

Expectations: MaxRotationSpeedChanged(current=self.current, _policy='wait')

command message olympe.messages.ardrone3.SpeedSettings.MaxVerticalSpeed(current, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettings.MaxVerticalSpeed

Set max vertical speed.

Parameters:
current (float) – Current max vertical speed in m/s

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Result: The max vertical speed is set. Then, event MaxVerticalSpeedChanged() is triggered.

Expectations: MaxVerticalSpeedChanged(current=self.current, _policy='wait')

command message olympe.messages.ardrone3.SpeedSettings.Outdoor(outdoor, _timeout=10, _no_expect=False, _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettings.Outdoor

Set outdoor mode.

Parameters:
outdoor (u8) – 1 if outdoor flight, 0 if indoor flight

_timeout (int) – command message timeout (defaults to 10)

_no_expect (bool) – if True for,do not expect the usual command expectation (defaults to False)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.SpeedSettings.Outdoor

Deprecated message

Warning

This message is deprecated and should no longer be used

Expectations: OutdoorChanged(outdoor=self.outdoor, _policy='wait')

event message olympe.messages.ardrone3.SpeedSettingsState.HullProtectionChanged(present=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettingsState.HullProtectionChanged

Presence of hull protection.

Parameters:
present (u8) – 1 if present, 0 if not present

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.SpeedSettingsState.HullProtectionChanged

Triggered by HullProtection().

event message olympe.messages.ardrone3.SpeedSettingsState.MaxPitchRollRotationSpeedChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettingsState.MaxPitchRollRotationSpeedChanged

Max pitch/roll rotation speed.

Parameters:
current (float) – Current max pitch/roll rotation speed in degree/s

min (float) – Range min of pitch/roll rotation speed

max (float) – Range max of pitch/roll rotation speed

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by MaxPitchRollRotationSpeed().

event message olympe.messages.ardrone3.SpeedSettingsState.MaxRotationSpeedChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettingsState.MaxRotationSpeedChanged

Max rotation speed.

Parameters:
current (float) – Current max yaw rotation speed in degree/s

min (float) – Range min of yaw rotation speed

max (float) – Range max of yaw rotation speed

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by MaxRotationSpeed().

event message olympe.messages.ardrone3.SpeedSettingsState.MaxVerticalSpeedChanged(current=None, min=None, max=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettingsState.MaxVerticalSpeedChanged

Max vertical speed.

Parameters:
current (float) – Current max vertical speed in m/s

min (float) – Range min of vertical speed

max (float) – Range max of vertical speed

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Supported by:

ANAFI:
with an up to date firmware

ANAFI Thermal:
with an up to date firmware

Triggered by MaxVerticalSpeed().

event message olympe.messages.ardrone3.SpeedSettingsState.OutdoorChanged(outdoor=None, _policy='check_wait', _float_tol=(1e-07, 1e-09))
ardrone3.SpeedSettingsState.OutdoorChanged

Outdoor mode.

Parameters:
outdoor (u8) – 1 if outdoor flight, 0 if indoor flight

_policy (olympe.arsdkng.expectations.ExpectPolicy) – specify how to check the expectation. Possible values are ‘check’, ‘wait’ and ‘check_wait’ (defaults to ‘check_wait’)

_float_tol (tuple) – specify the float comparison tolerance, a 2-tuple containing a relative tolerance float value and an absolute tolerate float value (default to (1e-07, 1e-09)). See python 3 stdlib math.isclose documentation for more information

Unsupported message

Todo

Remove unsupported message ardrone3.SpeedSettingsState.OutdoorChanged

Deprecated message

Warning

This message is deprecated and should no longer be used