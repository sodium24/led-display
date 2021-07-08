################################################################################
# controller_base.py
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
    """
    Base class to be implemented by all controllers
    """
    def __init__(self, config, main_app):
        """
        Initialize a controller
        """
        self.config = config
        self.main_app = weakref.ref(main_app)
        self.controller_thread = None
        self.stop_event = threading.Event()

    def start(self):
        """
        Start the controller running
        """
        self.controller_thread = threading.Thread(target=self.run)
        self.controller_thread.daemon = True
        self.controller_thread.start()

    def stop(self):
        """
        Stop a running controller
        """
        if self.controller_thread is not None:
            self.stop_event.set()
            self.controller_thread.join()
            self.controller_thread = None

    def get_state(self):
        """
        Controller function to retrieve the app state
        """
        return self.main_app().get_state()

    def get_screen_order(self):
        """
        Controller function to retrieve screen order
        """
        return self.main_app().screen_order

    def set_screen_order(self, screen_order):
        """
        Controller function to set screen order
        """
        self.main_app().screen_order = screen_order
        return True

    def save_screen_order(self, screen_order):
        """
        Controller function to set and save screen order
        """
        self.main_app().screen_order = screen_order
        self.main_app().save_screen_order(self.main_app().config_directory, screen_order)
        return True

    def get_config(self):
        """
        Controller function to retrieve configuration
        """
        return self.main_app().config

    def set_config(self, config):
        """
        Controller function to set configuration
        """
        self.main_app().config = config
        self.main_app().reload_running_app()
        return True

    def save_config(self, config):
        """
        Controller function to set and save configuration
        """
        self.main_app().config = config
        self.main_app().reload_running_app()
        self.main_app().save_system_config(self.main_app().config_directory, config)
        return True

    def send_input_event(self, input_event):
        """
        Controller function to inject an input event
        """
        return self.main_app().on_input_event(input_event)

    def send_joystick_press(self, button, button_states):
        """
        Controller function to inject a joystick button press
        """
        return self.main_app().on_joystick_press(button, button_states)

    def send_joystick_release(self, button, button_states):
        """
        Controller function to inject a joystick button release
        """
        return self.main_app().on_joystick_release(button, button_states)

    def send_joystick_axis(self, axis_states):
        """
        Controller function to inject joystick axis data
        """
        return self.main_app().on_joystick_axis(axis_states)

    def enter_sleep_mode(self):
        """
        Controller function to turn off the LED display
        """
        self.main_app().enter_sleep_mode()

    def start_app_by_name(self, screen_name):
        """
        Controller function to start an app by the screen name
        """
        return self.main_app().start_app_by_name(screen_name)

    def stop_app(self):
        """
        Controller function to stop a running app
        """
        return self.main_app().stop_running_app()

    def run(self):
        """
        Main controller run routine, to be implemented by the controller
        """
        return
