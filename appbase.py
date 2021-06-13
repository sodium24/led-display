import argparse
import time
import sys
import os
import appcontrols
import weakref
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics

class AppBase(object):
    def __init__(self, config, app_config, loaded_fonts, matrix=None, parent=None):
        self.config = config
        self.app_config = app_config
        self.loaded_fonts = loaded_fonts
        self.stop_flag = False
        self.controls = {}
        self.control_classes = {
            "fill": appcontrols.FillControl,
            "text": appcontrols.TextControl,
            "image": appcontrols.ImageControl,
            "rect": appcontrols.RectControl,
        }
        self.matrix = matrix
        self.next_z_index = 0
        self.on_app_exit = None

        # To enable running a child app
        self.running_app = None
        self.parent_app = None

        if parent is not None:
            self.parent_app = weakref.ref(parent)

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
        screen_app = self.config["screens"][screen_name]
        screen_class = addons.apps[screen_app["app"]]
        app_config = screen_app.get("config", {})
        self.running_app = screen_class(self.config, app_config, self.loaded_fonts, matrix=self.matrix, parent=self)
        try:
            print("Starting app for screen " + screen_name)
            print("Press CTRL-C to stop...")
            self.running_app.start()
            print("Execution complete")
        except Exception as err:
            print("Exception while running app: %s" % err)

        self.running_app = None

    def stop(self):
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
