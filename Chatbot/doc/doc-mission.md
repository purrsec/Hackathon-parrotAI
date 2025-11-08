How to use AirSDK missions
To run a custom mission, the first step is to launch Parrot Sphinx with a drone supporting AirSDK.

For some missions, it may be necessary for the drone to have access to the Internet. In that case, the simulated drone needs to be started with the option ::wan_access=1. It is also advised to keep the simulated clocks in rtc mode (see Clocks in Parrot Sphinx). This way, there will not be any clock drift between the remove server(s) and the drone from the RTC clock perspective.

sphinx <my.drone>::wan_access=1
Unlike with the real drone, there is no security setup required.

The mission package needs to be built with the pc variant of the SDK.

There are two ways to upload the mission and restart the drone:

From a mission workspace:

./build.sh -p pc -t sync --reboot --is-default
If you only have access to a signed archive:

Upload the mission:

curl -i -X PUT "http://anafi-ai.local/api/v1/mission/missions/?allow_overwrite=yes&allow_unsigned=yes" --data-binary @"/path/to/your/mission-pc.tar.gz"
Then reboot and check that the mission is listed.

curl -i -X PUT "http://anafi-ai.local/api/v1/system/reboot"
curl -i "http://anafi-ai.local/api/v1/mission/missions"
Once the drone is restarted, you just need to pursue like with a real drone, following the AirSDK documentation.