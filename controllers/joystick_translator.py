################################################################################
# joystick_translator.py
#-------------------------------------------------------------------------------
# Translator class for a joystick to generate input events.
# Tested on an XBox one controller.
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

class JoystickTranslator(object):
    def __init__(self):
        self.current_action = (None, 0.0)
        self.button_states = {}

    def on_joystick_press(self, button, button_states):
        self.button_states = dict(button_states)
        return None

    def on_joystick_release(self, button, button_states):
        input_event = None
        if button == "a" and self.button_states.get("a"):
            input_event = "select"
        if button == "b" and self.button_states.get("b"):
            input_event = "exit"
        self.button_states = dict(button_states)
        return input_event

    def on_joystick_axis(self, axis_states):
        input_event = None
        max_axis = None
        max_val = 0.0
        for axis in ["x", "y", "z", "rz", "hat0x", "hat0y"]:
            if abs(axis_states[axis]) > max_val:
                max_val = abs(axis_states[axis])
                max_axis = axis

        if max_axis is None:
            self.current_action = (None, 0.0)
            return input_event

        if max_axis == self.current_action[0] and abs(axis_states[max_axis]) < 0.5:
            if self.current_action[0] in ["x", "z", "hat0x"] and self.current_action[1] > 0:
                input_event = "right"
            elif self.current_action[0] in ["x", "z", "hat0x"] and self.current_action[1] < 0:
                input_event = "left"
            elif self.current_action[0] in ["y", "rz", "hat0y"] and self.current_action[1] > 0:
                input_event = "down"
            elif self.current_action[0] in ["y", "rz", "hat0y"] and self.current_action[1] < 0:
                input_event = "up"
            self.current_action = (None, 0.0)
        elif abs(axis_states[max_axis]) > abs(self.current_action[1]) and abs(axis_states[max_axis]) > 0.5:
            self.current_action = (max_axis, axis_states[max_axis])

        return input_event
