################################################################################
# joystick_controller.py
#-------------------------------------------------------------------------------
# Controller class to allow a joystick (such as an XBox controller) to interact
# with the LED display.
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

import os
import time
import fcntl
import weakref
from controllers.joystick_device import Joystick
from controller_base import ControllerBase

def has_js():
    """
    Check if a joystick is present
    """

    for filename in os.listdir('/dev/input'):
        if filename.startswith('js'):
            return True

    return False

class JoystickController(ControllerBase):
    """
    Controller for a joystick to interact with the LED display
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the joystick controller
        """
        super(JoystickController, self).__init__(*args, **kwargs)

    def run(self):
        """
        Main joystick controller run loop, to keep detecting joystick
        presence, and when it connects, listen for input events
        """
        while not self.stop_event.wait(1.0):

            # Wait for the joystick to show up
            while not has_js() and not self.stop_event.wait(1.0):
                continue

            # Exit if terminated
            if self.stop_event.is_set():
                break

            jsdev = None

            try:
                jsdev = Joystick("/dev/input/js0")
                jsdev.on_press = self.send_joystick_press
                jsdev.on_release = self.send_joystick_release
                jsdev.on_axis = self.send_joystick_axis

                # Continue while the joystick exists
                while has_js() and not jsdev.failed and not self.stop_event.wait(1.0):
                    continue
            except Exception as err:
                print("Exception" + str(err))
       
            if jsdev:
                # Terminate the joystick

                jsdev.on_press = None
                jsdev.on_release = None
                jsdev.on_axis = None
                jsdev.terminate()
