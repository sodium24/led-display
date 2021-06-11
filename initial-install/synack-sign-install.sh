#!/bin/bash
#
# This script is used to perform the initial setup of your Synack LED sign.
# It will clone the git repo with the control software, setup program
# defaults, and run the Adafruit script to configure the LED Matrix Bonnet.

cd ~
sudo apt-get update
sudo apt-get install -y git

git clone https://github.com/sodium24/led-display

# Setup the default Synack sign configuration
sudo bash ~/led-display/initial-install/synack-restore-defaults.sh

# Run the Adafruit Matrix Bonnet install script for first-time setup
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh > ~/led-display/initial-install/adafruit-setup.sh
sudo bash ~/led-display/initial-install/adafruit-setup.sh

# Done!
