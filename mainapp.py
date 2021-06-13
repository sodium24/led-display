################################################################################
# mainapp.py
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
import os
import addons
import appbase
import joystick_translator

class MainApp(appbase.AppBase):
    def __init__(self, json_file):
        # Cache of loaded fonts
        self.loaded_fonts = {}

        # Load the JSON configuration file
        self.json_file = json_file
        with open(self.json_file) as f:
            config = json.loads(f.read())

        # AppBase initialization
        super(MainApp, self).__init__(config, config, self.loaded_fonts)

        self.config = config
        self.current_screen_index = -1
        self.current_screen_name = ""
        self.screen_index = 0
        self.restart_app = False

        # Translate joystick data to input events
        self.joystick_translator = joystick_translator.JoystickTranslator()

        # Load controllers
        self.controllers = []
        for controller_name in addons.controllers:
            print("Starting controller %s..." % controller_name) 
            controller = addons.controllers[controller_name](self.config, self)
            controller.start()
            self.controllers += [controller]

    def get_state(self):
        return {"screenIndex": self.current_screen_index, "screenName": self.current_screen_name}

    def save_config(self):
        try:
            os.unlink(self.json_file + ".bak")
        except Exception:
            pass
        try:
            os.rename(self.json_file, self.json_file + ".bak")
        except Exception:
            pass
        with open(self.json_file, "w") as f:
            f.write(json.dumps(self.config, indent=4))

    def on_input_event(self, input_event):
        handled = False

        if not handled and self.running_app is not None:
            handled = self.running_app.on_input_event(input_event)

        if not handled:
            if input_event == "right":
                self.screen_index += 1
                self.screen_index %= len(self.config["screenOrder"])
                self.stop_running_app()
                handled = True
            elif input_event == "left":
                self.screen_index -= 1
                self.screen_index %= len(self.config["screenOrder"])
                self.stop_running_app()
                handled = True

        if not handled:
            handled = super(MainApp, self).on_input_event(input_event)

        return handled

    def on_joystick_press(self, button, button_states):
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
        if self.running_app:
            def on_app_exit(app):
                self.matrix.Clear()

            self.running_app.on_app_exit = on_app_exit
            self.stop_running_app()
        else:
            self.matrix.Clear()

    def stop_running_app(self):
        if self.running_app is not None:
            self.running_app.stop()

    def reload_running_app(self):
        self.restart_app = True

    def _start_app(self, index):
        self.current_screen_index = self.screen_index = index
        screen_name = self.config["screenOrder"][self.screen_index]
        self.current_screen_name = screen_name
        self._start_app_by_name(screen_name)

    def wait_for_complete(self):
        while self.running_app:
            time.sleep(1)

    def run(self):
        while True:
            if self.current_screen_index != self.screen_index or self.restart_app:
                self.stop_running_app()
                self.restart_app = False
                self._start_app(self.screen_index)
            else:
                time.sleep(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: %s <config_json_file>" % sys.argv[0])
        exit(1)

    main_app = MainApp(sys.argv[1])
    main_app.start()

if __name__ == "__main__":
    main()
