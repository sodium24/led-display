################################################################################
# main_app.py
#-------------------------------------------------------------------------------
# Application framework for running apps on an LED display.
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

import sys
import json
import threading
import time
import signal
import os
from . import addons
from .app_base import AppBase
from .controllers.joystick_translator import JoystickTranslator

class MainApp(AppBase):
    """
    Main app which runs at startup and allows other apps to be run based on user input
    """
    def __init__(self):
        self.terminate_event = threading.Event()

        # Cache of loaded fonts
        self.loaded_fonts = {}

        config_directory = os.getenv("LED_DISPLAY_CONFIG")
        if config_directory is None:
            config_directory = os.path.join(os.getcwd(), "config")

        system_config = self.load_system_config(config_directory)
        app_list = self.enumerate_screen_names(config_directory)
        for screen_name in app_list:
            self.load_app_config(config_directory, screen_name)

        # Order of screens to display
        screen_order_path = os.path.join(config_directory, "screen_order.txt")
        screen_order_list = []
        with open(screen_order_path) as f:
            line = f.readline().replace("\r", "").replace("\n", "")
            while line:
                screen_order_list += [line]
                line = f.readline().replace("\r", "").replace("\n", "")

        # AppBase initialization
        super(MainApp, self).__init__(system_config, {}, self.loaded_fonts, config_directory=config_directory)

        # Check if display should turn on at boot?
        self.off_at_boot = system_config["settings"]["displayOffAfterBoot"]

        self.screen_order = screen_order_list
        self.current_screen_index = -1
        self.current_screen_name = ""
        self.screen_index = 0
        self.restart_app = False

        # Translate joystick data to input events
        self.joystick_translator = JoystickTranslator()

        # Load controllers
        self.controllers = []
        for controller_name in addons.controllers:
            print("Starting controller %s..." % controller_name) 
            controller = addons.controllers[controller_name](self.config, self)
            controller.start()
            self.controllers += [controller]

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        """
        Catch a SIGINT or SIGTERM to exit gracefully
        """
        self.terminate_event.set()
        self.stop_running_app()

    def save_screen_order(self, config_directory, screen_order):
        """
        Save an updated screen order list to the filesystem
        """
        screen_order_path = os.path.join(config_directory, "screen_order.txt")
        with open(screen_order_path, "w") as f:
            f.writelines(screen_order)

    def get_state(self):
        """
        Retrieve the current app state
        """
        return {"screenIndex": self.current_screen_index, "screenName": self.current_screen_name}

    def on_input_event(self, input_event):
        """
        Handle an input event. Return true if handled.
        """
        handled = False

        if self.off_at_boot:
            self.off_at_boot = False
            handled = True

        if not handled and self.running_app is not None:
            handled = self.running_app.on_input_event(input_event)

        if not handled:
            if input_event == "right":
                self.start_app_by_id((self.screen_index + 1) % len(self.screen_order))
                handled = True
            elif input_event == "left":
                self.start_app_by_id((self.screen_index - 1) % len(self.screen_order))
                handled = True

        if not handled:
            handled = super(MainApp, self).on_input_event(input_event)

        if not handled:
            if not self.running_app:
                self.reload_running_app()

        return handled

    def on_joystick_press(self, button, button_states):
        """
        Handle a joystick button press. Return true if handled.
        """
        handled = False

        input_event = self.joystick_translator.on_joystick_press(button, button_states)

        if not handled and self.running_app is not None:
            handled = self.running_app.on_joystick_press(button, button_states)

        if not handled:
            handled = super(MainApp, self).on_joystick_press(button, button_states)

        if not handled and input_event is not None:
            return self.on_input_event(input_event)

        return handled

    def on_joystick_release(self, button, button_states):
        """
        Handle a joystick button release. Return true if handled.
        """
        handled = False

        input_event = self.joystick_translator.on_joystick_release(button, button_states)

        if not handled and self.running_app is not None:
            handled = self.running_app.on_joystick_release(button, button_states)

        if not handled:
            handled = super(MainApp, self).on_joystick_release(button, button_states)

        print("on_joystick_release", input_event)

        if not handled and input_event is not None:
            return self.on_input_event(input_event)

        return handled

    def on_joystick_axis(self, axis_states):
        """
        Handle a joystick axis event. Return true if handled.
        """
        handled = False

        input_event = self.joystick_translator.on_joystick_axis(axis_states)

        if not handled and self.running_app is not None:
            handled = self.running_app.on_joystick_axis(axis_states)

        if not handled:
            handled = super(MainApp, self).on_joystick_axis(axis_states)

        if not handled and input_event is not None:
            return self.on_input_event(input_event)

        return handled

    def enter_sleep_mode(self):
        """
        Used for entering a sleep mode where the LED panel is turned off
        """
        if self.running_app:
            def on_app_exit(app):
                self.matrix.Clear()

            self.running_app.on_app_exit = on_app_exit
            self.stop_running_app()
        else:
            self.matrix.Clear()

    def start_app_by_id(self, index):
        """
        Start an app based on the screen order index in "screen_order.txt"
        """
        self.current_screen_index = self.screen_index = index
        screen_name = self.screen_order[self.screen_index]
        self.start_app_by_name(screen_name)

    def start_app_by_name(self, screen_name):
        """
        Start an app based on the screen name
        """
        self.screen_name = screen_name
        self.stop_running_app()

    def stop_running_app(self):
        """
        Attempt to stop the current running child app
        """
        if self.running_app is not None:
            self.running_app.stop()

    def reload_running_app(self):
        """
        Attempt to reload the current running child app once stopped
        """
        self.restart_app = True

    def wait_for_complete(self):
        """
        Wait for the current child app to finish stopping
        """
        while self.running_app:
            time.sleep(1)

    def app_kill_thread(self, timeout):
        """
        Kill a running app after a timeout
        """
        time.sleep(timeout)
        self.stop_running_app()

    def run(self):
        """
        Main routine to start up child apps as needed
        """
        load_screen_app = self.config["settings"].get("loadScreenApp", "")

        if len(load_screen_app) > 0:
            # Show the load screen for 10 seconds
            load_screen_kill = threading.Thread(target=self.app_kill_thread,args=(30.0,))
            load_screen_kill.daemon = True
            load_screen_kill.start()

            self._start_app_by_name(load_screen_app)

            load_screen_kill.join()

        self.matrix.Clear()

        while not self.terminate_event.is_set():
            if not self.off_at_boot and (self.current_screen_name != self.screen_name or self.restart_app):
                self.stop_running_app()
                self.restart_app = False
                self.current_screen_name = self.screen_name
                self._start_app_by_name(self.screen_name)
            else:
                self.terminate_event.wait(1.0)

def main():
    """
    Begin main app execution
    """
    main_app = MainApp()
    main_app.start()

if __name__ == "__main__":
    main()
