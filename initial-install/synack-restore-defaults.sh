#!/bin/bash
#
# This script can be run anytime to restore the default configuration
# of your Synack LED sign. It will copy the default start.sh script to your
# home directory, and ensure the led-display service is installed so it
# will run at system boot.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

service led-display stop

ln -s $SCRIPT_DIR/synack-restore-defaults.sh ~/led-display-restore-defaults.sh

cp -f $SCRIPT_DIR/synack-startup.sh ~/led-display-startup.sh
chmod 755 ~/led-display-startup.sh

cp -f $SCRIPT_DIR/led-display.service /etc/systemd/system/
systemctl enable led-display

cp -rf $SCRIPT_DIR/synack-config ~/

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
printf "Please enter your alias: "
read user_alias
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
printf "[1-4]: "
read config_selection

echo "Changes have been saved! Please reboot or run 'sudo service led-display start' to continue."

