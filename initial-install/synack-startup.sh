#!/bin/bash
#
# This script will be copied into your home directory as ~/led-sign-startup.sh.
# Any modifications can be made to that file as desired. 
#
# The original is stored in the `initial-install` directory, and should generally
# not be modified. It can be be restored by running the `synack-restore-defaults.sh`
# script.

# Run the joystick controller
python /home/pi/led-display/controllers/joystick_controller.py &

# Run the default startup program!
sudo python /home/pi/led-display/mainapp.py /home/pi/synack-config.json
