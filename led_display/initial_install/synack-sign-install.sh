#!/bin/bash

################################################################################
# SYNACK LED SIGN SETUP
#
# synack-sign-install.sh
#-------------------------------------------------------------------------------
#
# This script is used to perform the initial setup of your Synack LED sign.
# It will clone the git repo with the control software, setup program
# defaults, and run the Adafruit script to configure the LED Matrix Bonnet.
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

cd /home/pi
sudo apt-get update
sudo apt-get install -y git

git clone https://github.com/sodium24/led-display

# Install the repo as a pip package "led_display"
# The -e option is used so that changes can be easily made to the package
cd /home/pi/led-display
sudo python -m pip install -e .

# Setup the default Synack sign configuration
sudo bash /home/pi/led-display/led_display/initial_install/synack-restore-defaults.sh

echo "--------------------------------------------------------------------------------"
echo ""
echo "The next portion of the installation will install the Adafruit Matrix Bonnet"
echo "related libraries. This may take some time (15 minutes or so), so please"
echo "be patient..." 
echo ""
echo "Note that the Synack LED Sign uses the LED Matrix Bonnet (option 1)."
echo ""
echo "By default only software PWM is supported, so unless you have upgraded this by"
echo "soldering a jumper on the Bonnet circuit board, please select \"CONVENIENCE\""
echo "instead of \"QUALITY\" when prompted."
echo ""
echo "--------------------------------------------------------------------------------"

sleep 30

cd /home/pi

# Run the Adafruit Matrix Bonnet install script for first-time setup
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh > /home/pi/adafruit-setup.sh
sudo bash /home/pi/adafruit-setup.sh

# Done!
