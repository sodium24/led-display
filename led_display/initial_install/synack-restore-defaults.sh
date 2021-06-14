#!/bin/bash

################################################################################
# SYNACK LED SIGN SETUP
#
# synack-restore-defaults.sh
#-------------------------------------------------------------------------------
#
# This script can be run anytime to restore the default configuration
# of your Synack LED sign. It will copy the default start.sh script to your
# home directory, and ensure the led-display service is installed so it
# will run at system boot.
# 
# By Malcolm Stagg
#
# Copyright (c) 2021 SODIUM-24, LLC
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

service led-display stop

# Add a symlink to the home directory for easy access to the script
ln -s $SCRIPT_DIR/synack-restore-defaults.sh /home/pi/led-display-restore-defaults.sh

# Install the startup script to the home directory
cp -pf $SCRIPT_DIR/synack-startup.sh /home/pi/led-display-startup.sh
chmod 755 /home/pi/led-display-startup.sh

# Install the startup service
cp -f $SCRIPT_DIR/led-display.service /etc/systemd/system/
systemctl enable led-display

# Copy the initial app/display configuration to the home directory
cp -rpf $SCRIPT_DIR/synack_config /home/pi/

echo '---------------------[ SYNACK LED SIGN ]--------------------'
echo ''
echo '          \`-.                /\                .-'"'"'/'
echo '           \   `-.           /  \           .-'"'"'   /'
echo '            `-.    `-,      /____\      .-'"'"'    .-'"'"''
echo '                `-.   \                /   .-'"'"''
echo '              \`-. \   \              /   / .-'"'"'/'
echo '               \   `    \            /    '"'"'   /'
echo '                `-.      \          /      .-'"'"''
echo '                    `-.   \        /   .-'"'"''
echo '                        `-.\      /.-'"'"''
echo '                   \`-.                .-'"'"'/'
echo '                    \   `-.        .-'"'"'   /'
echo '                     `-.    `-,,-'"'"'    .-'"'"''
echo '                         `-,      ,-'"'"''
echo '                         /'"'"'  .--.  `'"'"''
echo '                        /.-'"'"'      `-.'"'"''
echo ''
echo ""
read -p "Please enter your alias: " user_alias
echo ""
echo "Hello $user_alias! Welcome to your Synack LED Sign!"
echo ""
echo "Please select the default sign mode:"
echo ""
echo "1) Normal logo display"
echo "2) Normal clock display"
echo "3) Personalized logo display"
echo "4) Personalized clock display"
echo ""

while ! [[ "$config_selection" =~ ^[1234]$ ]]; do
    read -p "[1-4]: " config_selection
done

if [ $config_selection == "1" ]; then
    ENABLE_CLOCK="false"
    ENABLE_ALIAS="false"
elif [ $config_selection == "2" ]; then
    ENABLE_CLOCK="true"
    ENABLE_ALIAS="false"
elif [ $config_selection == "3" ]; then
    ENABLE_CLOCK="false"
    ENABLE_ALIAS="true"
else
    ENABLE_CLOCK="true"
    ENABLE_ALIAS="true"
fi

sed "s/{SHOW_ALIAS}/$ENABLE_ALIAS/g; s/{SHOW_CLOCK}/$ENABLE_CLOCK/g" /home/pi/synack_config/apps/synack_display.json.in > /home/pi/synack_config/apps/synack_display.json
rm /home/pi/synack_config/apps/synack_display.json.in

echo "Changes have been saved! Please reboot or run 'sudo service led-display start' to continue."
echo ""
echo "If you wish to reconfigure your sign, run '/home/pi/led-display-restore-defaults.sh' anytime"
echo "or manually make changes in the /home/pi/synack_config directory"

