import argparse
import time
import sys
import os
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics

class AppBase(object):
    def __init__(self, config, app_config, loaded_fonts):
        self.config = config
        self.app_config = app_config
        self.loaded_fonts = loaded_fonts
        self.stopFlag = False

    def load_font(self, font_name):
        if font_name not in self.loaded_fonts:
            self.loaded_fonts[font_name] = graphics.Font()
            self.loaded_fonts[font_name].LoadFont(self.config["fonts"][font_name]["path"])
            if self.config["fonts"][font_name].get("outline"):
                self.loaded_fonts[font_name] = self.loaded_fonts[font_name].CreateOutlineFont()
        return self.loaded_fonts[font_name]

    def get_text_width(self, text, font):
        width = 0
        for character in text:
            width += font.CharacterWidth(ord(character))
        return width

    def run(self):
        return

    def stop(self):
        self.stopFlag = True

    def start(self):
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

        self.run()

        return True
