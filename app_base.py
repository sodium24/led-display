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
import app_controls
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics

class AppBase(object):
    def __init__(self, config, app_config, loaded_fonts, matrix=None, parent=None, config_directory=None):
        self.config = config
        self.app_config = app_config
        self.loaded_fonts = loaded_fonts
        self.stop_flag = False
        self.controls = {}
        self.control_classes = {
            "fill": app_controls.FillControl,
            "text": app_controls.TextControl,
            "image": app_controls.ImageControl,
            "rect": app_controls.RectControl,
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
        system_json_path = os.path.join(config_directory, "system.json")
        with open(system_json_path) as f:
            system_config = json.loads(f.read())
        return system_config

    def enumerate_screen_names(self, config_directory):
        app_list = []
        apps_path = os.path.join(config_directory, "apps")
        for filename in os.listdir(apps_path):
            if os.path.splitext(filename)[1].lower() == ".json":        
                app_list += [os.path.splitext(filename)[0]]

        return app_list

    def load_app_config(self, config_directory, screen_name):
        apps_path = os.path.join(config_directory, "apps")
        app_json_path = os.path.join(apps_path, screen_name + ".json")
        with open(app_json_path) as f:
            return json.loads(f.read())

    def load_font(self, font_name):
        if font_name not in self.loaded_fonts:
            self.loaded_fonts[font_name] = graphics.Font()
            self.loaded_fonts[font_name].LoadFont(self.config["fonts"][font_name]["path"])
            if self.config["fonts"][font_name].get("outline"):
                self.loaded_fonts[font_name] = self.loaded_fonts[font_name].CreateOutlineFont()
        return self.loaded_fonts[font_name]

    def create_control(self, control_type, control_id):
        self.controls[control_id] = self.control_classes[control_type](control_id, self)
        self.controls[control_id].z_index = self.next_z_index
        self.next_z_index += 1
        return self.controls[control_id]

    def get_control(control_id):
        return self.controls.get(control_id)

    def _delete_control(control_id):
        if control_id in self.controls:
            del self.controls[control_id]

    def get_state(self):
        return {}

    def update(self, directToMatrix = False):
        canvas = self.matrix if directToMatrix else self.offscreen_canvas

        sorted_controls = sorted(self.controls.items(), key=lambda kv: kv[1].z_index)
        for control in sorted_controls:
            if control[1].enabled:
                control[1].on_frame()
                control[1].draw(canvas)

    def is_static(self):
        static = True

        for control in self.controls.items():
            if control[1].enabled and not control[1].static:
                static = False
                break

        return static

    def draw(self):
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
        self.offscreen_canvas.Clear()

    def enter_sleep_mode(self):
        if self.parent_app is not None:
            self.parent_app().enter_sleep_mode()

    def on_input_event(self, input_event):
        if input_event == "exit":
            self.stop()
            handled = True
        return False

    def on_joystick_press(self, button, button_states):
        return False

    def on_joystick_release(self, button, button_states):
        return False

    def on_joystick_axis(self, axis_states):
        return False

    def run(self):
        return

    def _start_app_by_name(self, screen_name):
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
        if self.parent_app is not None:
            self.stop_flag = True

    def start(self):
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
