
Olympe
Olympe is a Python3 module belonging to Parrot Ground SDK. It allows you to easily write Python scripts to control the drone using the virtual Ethernet interface.

Here is an example requesting the drone to take off, then to land.

import olympe
import time
import olympe.messages.ardrone3.Piloting as piloting

DRONE_IP="10.202.0.1"

drone = olympe.Drone(DRONE_IP)
drone.connect()
assert drone(piloting.TakeOff()).wait().success()
time.sleep(12)
assert drone(piloting.Landing()).wait().success()
drone.disconnect()
Note

You can also use Olympe with a Wi-Fi interface and/or with a real drone.