################################################################################
# app_base.py
#-------------------------------------------------------------------------------
# Base class for an app running on the LED display application framework.
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

import argparse
import time
import sys
import os
import json
import weakref
import threading
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics
 
from . import app_controls
from . import synack_controls

class AppBase(object):
    """
    Base class to be implemented by all apps
    """
    def __init__(self, config, app_config, loaded_fonts, matrix=None, parent=None, config_directory=None):
        """
        Initialize a running app
        """
        self.config = config
        self.app_config = app_config
        self.loaded_fonts = loaded_fonts
        self.stop_event = threading.Event()
        self.controls = {}
        self.control_classes = {
            "fill": app_controls.FillControl,
            "text": app_controls.TextControl,
            "image": app_controls.ImageControl,
            "rect": app_controls.RectControl,
            "synack_load": synack_controls.SynackLoadAnimationControl,
        }
        self.matrix = matrix
        self.config_directory = config_directory
        self.next_z_index = 0
        self.on_app_exit = None

        # To enable running a child app
        self.running_app = None
        self.parent_app = None

        if parent is not None:
            self.parent_app = weakref.ref(parent)

    def load_system_config(self, config_directory):
        """
        Load the system configuration from the JSON config file "$LED_DISPLAY_CONFIG/system.json"
        """
        system_json_path = os.path.join(config_directory, "system.json")
        with open(system_json_path) as f:
            system_config = json.loads(f.read())
        return system_config

    def save_system_config(self, config_directory, system_config):
        """
        Save the system configuration to the JSON config file "$LED_DISPLAY_CONFIG/system.json"
        """
        system_json_path = os.path.join(config_directory, "system.json")
        with open(system_json_path, "w") as f:
            system_config = f.write(json.dumps(system_config, indent=4))
        return system_config

    def enumerate_screen_names(self, config_directory):
        """
        Enumerate the configured app screen names from "$LED_DISPLAY_CONFIG/apps"
        """
        app_list = []
        apps_path = os.path.join(config_directory, "apps")
        for filename in os.listdir(apps_path):
            if os.path.splitext(filename)[1].lower() == ".json":        
                app_list += [os.path.splitext(filename)[0]]

        return app_list

    def load_app_config(self, config_directory, screen_name):
        """
        Load an app configuration by screen name from "$LED_DISPLAY_CONFIG/apps"
        """
        try:
            apps_path = os.path.join(config_directory, "apps")
            app_json_path = os.path.join(apps_path, screen_name + ".json")
            with open(app_json_path) as f:
                return json.loads(f.read())
        except Exception as err:
            raise Exception("Exception reading app config for screen_name=\"%s\": %s" % (screen_name, err))

    def load_font(self, font_name, outline=False):
        """
        Load a font by name, as specified in "$LED_DISPLAY_CONFIG/system.json"
        """
        if (font_name, False) not in self.loaded_fonts:
            for path in self.config["fonts"]["paths"]:
                font_path = os.path.join(path, font_name + ".bdf")
                if os.path.exists(font_path):
                    self.loaded_fonts[(font_name, False)] = graphics.Font()
                    self.loaded_fonts[(font_name, False)].LoadFont(font_path)

        if outline:
            if (font_name, True) not in self.loaded_fonts:
                self.loaded_fonts[(font_name, True)] = self.loaded_fonts[(font_name, False)].CreateOutlineFont()

            font = self.loaded_fonts[(font_name, True)]
        else:
            font = self.loaded_fonts[(font_name, False)]

        return font

    def create_control(self, control_type, control_id):
        """
        Create a graphical control by type. See app_controls.py for a list of supported types.
        """
        self.controls[control_id] = self.control_classes[control_type](control_id, self)
        self.controls[control_id].z_index = self.next_z_index
        self.next_z_index += 1
        return self.controls[control_id]

    def get_control(control_id):
        """
        Retrieve a graphical control by name
        """
        return self.controls.get(control_id)

    def _delete_control(control_id):
        """
        Delete a graphical control by name
        """
        if control_id in self.controls:
            del self.controls[control_id]

    def get_state(self):
        """
        Retrieve a current state from the application
        """
        return {}

    def is_static(self):
        """
        Returns whether the current list of controls correspond to a static display,
        i.e. one where frequent refreshing of the display is not necessary.
        """
        static = True

        for control in self.controls.items():
            if control[1].enabled and not control[1].static:
                static = False
                break

        return static

    def update(self, directToMatrix = False):
        """
        Update the canvas (or matrix) with graphical control data. This should generally 
        be called before "draw", which will update the matrix with current canvas data.
        """
        canvas = self.matrix if directToMatrix else self.offscreen_canvas

        sorted_controls = sorted(self.controls.items(), key=lambda kv: kv[1].z_index)
        for control in sorted_controls:
            if control[1].enabled:
                control[1].on_frame()
                control[1].draw(canvas)

    def draw(self):
        """
        Transfer contents of the canvas to the display. This should generally
        be called after "update".
        """
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
        self.offscreen_canvas.Clear()

    def enter_sleep_mode(self):
        """
        Used for entering a sleep mode where the LED panel is turned off
        """
        if self.parent_app is not None:
            self.parent_app().enter_sleep_mode()

    def on_input_event(self, input_event):
        """
        Handle an input event. Return true if handled.
        """
        if input_event == "exit":
            self.stop()
            handled = True
        return False

    def on_joystick_press(self, button, button_states):
        """
        Handle a joystick button press. Return true if handled.
        """
        return False

    def on_joystick_release(self, button, button_states):
        """
        Handle a joystick button release. Return true if handled.
        """
        return False

    def on_joystick_axis(self, axis_states):
        """
        Handle a joystick axis event. Return true if handled.
        """
        return False

    def run(self):
        """
        Main app run routine, to be implemented by the application
        """
        return

    def _start_app_by_name(self, screen_name):
        """
        Starts a child app running by name. This will block until the app exits.
        """
        import addons
        app_config = self.load_app_config(self.config_directory, screen_name)
        screen_class = addons.apps[app_config["app"]]
        self.running_app = screen_class(self.config, app_config.get("config", {}), self.loaded_fonts, matrix=self.matrix, parent=self, config_directory=self.config_directory)
        try:
            print("Starting app for screen " + screen_name)
            print("Press CTRL-C to stop...")
            self.running_app.start()
            print("Execution complete for screen " + screen_name)
        except Exception as err:
            print("Exception while running app: %s" % err)

        self.running_app = None

    def stop(self):
        """
        Attempt to stop the current app
        """
        self.stop_event.set()

    def start(self):
        """
        Setup routine which is called before "run"
        """
        if self.matrix is None:
            options = RGBMatrixOptions()

            if self.config["display"].get("ledGpioMapping") != None:
                options.hardware_mapping = self.config["display"]["ledGpioMapping"]
            options.rows = self.config["display"]["ledRows"]
            options.cols = self.config["display"]["ledCols"]
            options.chain_length = self.config["display"]["ledChain"]
            options.parallel = self.config["display"]["ledParallel"]
            options.row_address_type = self.config["display"]["ledRowAddrType"]
            options.multiplexing = self.config["display"]["ledMultiplexing"]
            options.pwm_bits = self.config["display"]["ledPwmBits"]
            options.brightness = self.config["display"]["ledBrightness"]
            options.pwm_lsb_nanoseconds = self.config["display"]["ledPwmLsbNanoseconds"]
            options.led_rgb_sequence = self.config["display"]["ledRgbSequence"]
            options.pixel_mapper_config = self.config["display"]["ledPixelMapper"]
            if self.config["display"]["ledShowRefresh"]:
                options.show_refresh_rate = 1

            if self.config["display"].get("ledSlowdownGpio") != None:
                options.gpio_slowdown = self.config["display"]["ledSlowdownGpio"]
            if self.config["display"].get("ledNoHardwarePulse") != None:
                options.disable_hardware_pulsing = self.config["display"]["ledNoHardwarePulse"]

            # Dropping privileges makes other things fail
            options.drop_privileges = False

            self.matrix = RGBMatrix(options = options)

        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.offscreen_canvas.Clear()

        try:
            self.run()
        except Exception as err:
            print("Exception while running app: %s" % err)

        if self.on_app_exit:
            self.on_app_exit(self)

        return True
