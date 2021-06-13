################################################################################
# controllerbase.py
#-------------------------------------------------------------------------------
# Base class for a controller to interact with the LED display application 
# framework.
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

import weakref
import threading

class ControllerBase(object):
    def __init__(self, config, main_app):
        self.config = config
        self.main_app = weakref.ref(main_app)
        self.controller_thread = None
        self.exit_flag = False

    def start(self):
        self.controller_thread = threading.Thread(target=self.run)
        self.controller_thread.daemon = True
        self.controller_thread.start()

    def stop(self):
        if self.controller_thread is not None:
            self.exit_flag = True
            self.controller_thread.join()
            self.controller_thread = None

    def get_state(self):
        return self.main_app().get_state()

    def get_config(self):
        return self.main_app().config

    def set_config(self, config):
        self.main_app().config = config
        self.main_app().reload_running_app()
        return True

    def save_config(self, config):
        self.main_app().config = config
        self.main_app().reload_running_app()
        self.main_app().save_config()
        return True

    def send_input_event(self, input_event):
        return self.main_app().on_input_event(input_event)

    def send_joystick_press(self, button, button_states):
        return self.main_app().on_joystick_press(button, button_states)

    def send_joystick_release(self, button, button_states):
        return self.main_app().on_joystick_release(button, button_states)

    def send_joystick_axis(self, axis_states):
        return self.main_app().on_joystick_axis(axis_states)

    def enter_sleep_mode(self):
        self.main_app().enter_sleep_mode()

    def run(self):
        return
