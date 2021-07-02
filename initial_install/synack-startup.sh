#!/bin/bash
#
# This script will be copied into your home directory as 
# '~/led-display-startup.sh'.
# Any modifications can be made to that file as desired. 
#
# The original is stored in the `initial_install` directory, and should
# generally not be modified. It can be be restored by running the
# '~/led-display-restore-defaults.sh' script.

sudo LED_DISPLAY_CONFIG=/home/pi/synack_config python -u -m led_display


