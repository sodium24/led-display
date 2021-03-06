################################################################################
# joystick_device.py
#-------------------------------------------------------------------------------
# Class to interface with a joystick, such as an XBox controller. 
#
# This is based on https://gist.github.com/rdb/8864666
# which was released by rdb under the Unlicense (unlicense.org)
# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt
#
# Modifications By Malcolm Stagg
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

import os, struct, array
import threading
from fcntl import ioctl

# These constants were borrowed from linux/input.h
axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'trottle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc',
}

button_names = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'a',
    0x131 : 'b',
    0x132 : 'c',
    0x133 : 'x',
    0x134 : 'y',
    0x135 : 'z',
    0x136 : 'tl',
    0x137 : 'tr',
    0x138 : 'tl2',
    0x139 : 'tr2',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',

    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}

class Joystick():
    """
    Joystick device interface
    """
    def __init__(self, name):
        """
        Initialize the joystick device. Handlers "on_press", "on_release",
        and "on_axis" can be set to receive joystick data.
        """
        self.name = name
        self.axis_states = {}
        self.button_states = {}
        self.axis_map = []
        self.button_map = []
        self.event_thread = None
        self.stop_event = threading.Event()
        self.failed = False

        self.on_press = None
        self.on_release = None
        self.on_axis = None

        self.event_thread = threading.Thread(target=self.event_loop)
        self.event_thread.daemon = True
        self.event_thread.start()

    def terminate(self):
        """
        Terminate the joystick device
        """
        self.stop_event.set()
        if self.event_thread:
            self.event_thread.join()

    def event_loop(self):
        """
        Main event loop to listen for joystick events
        """
        try:
            print('Opening %s...' % self.name)
            with open(self.name, 'rb') as jsdev:
                print('Opened %s' % self.name)

                # Get number of axes and buttons.
                buf = array.array('B', [0])
                ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
                self.num_axes = buf[0]

                buf = array.array('B', [0])
                ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
                self.num_buttons = buf[0]

                # Get the axis map.
                buf = array.array('B', [0] * 0x40)
                ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

                for axis in buf[:self.num_axes]:
                    axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
                    self.axis_map.append(axis_name)
                    self.axis_states[axis_name] = 0.0

                # Get the button map.
                buf = array.array('H', [0] * 200)
                ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

                for btn in buf[:self.num_buttons]:
                    btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
                    self.button_map.append(btn_name)
                    self.button_states[btn_name] = 0

                print('%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map)))
                print('%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map)))

                while not self.stop_event.is_set():
                    evbuf = jsdev.read(8)
                    if evbuf:
                        time, value, type, number = struct.unpack('IhBB', evbuf)

                        if type & 0x01:
                            button = self.button_map[number]
                            if button and self.button_states.get(button) != value:
                                self.button_states[button] = value
                                if value:
                                    print("%s pressed" % (button))
                                    if self.on_press:
                                        self.on_press(button, self.button_states)
                                else:
                                    print("%s released" % (button))
                                    if self.on_release:
                                        self.on_release(button, self.button_states)

                        axis_updated = False
                        if type & 0x02:
                            axis = self.axis_map[number]
                            fvalue = value / 32767.0
                            if axis and self.axis_states.get(axis) != fvalue:
                                self.axis_states[axis] = fvalue
                                #print("%s: %.3f" % (axis, fvalue))
                                axis_updated = True

                        if axis_updated and self.on_axis:
                            self.on_axis(self.axis_states)

        except Exception as err:
            print("Exception: %s" % err)
            self.failed = True
                        
