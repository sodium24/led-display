################################################################################
# synack_controls.py
#-------------------------------------------------------------------------------
# Control elements an app may use to simplify interacting with the LED display 
# directly.
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
import os
from PIL import Image
from rgbmatrix import graphics
from .app_controls import Control

def compute_alpha(alpha_min, alpha_max, frame_num, frame_max):
    frame_num = min(frame_num, frame_max-frame_num)
    if float(frame_num)/frame_max <= 0.4:
        alpha_percent = (float(frame_num)/frame_max) / 0.4
    elif float(frame_num)/frame_max >= 0.7:
        alpha_percent = 0.0
    else:
        alpha_percent = 1.0 - ((float(frame_num)/frame_max - 0.4) / 0.3)
    alpha = min(
        alpha_max, 
        max(
            alpha_min, 
            int(alpha_min + alpha_percent * (alpha_max-alpha_min))
        )
    )
    return alpha

class SynackLoadAnimationControl(Control):
    """
    Control for displaying the Synack load animation
    """
    def __init__(self, control_id, app_base):
        """
        Initialize the control with an ID and app reference
        """
        super(SynackLoadAnimationControl, self).__init__(control_id, app_base)
        self._path = ""
        self._x = 0
        self._y = 0
        self._frame_num = 0
        self._width = 0
        self._height = 0
        self._frames = []
        self._bkg = None
        self._load_1 = None
        self._load_2 = None
        self._load_3 = None
        self._load_4 = None
        self._load_1_weighted = None
        self._load_2_weighted = None
        self._load_3_weighted = None
        self._load_4_weighted = None

    def set_path(self, path):
        """
        Set resource path
        """
        if path != self._path:
            self._path = path
            self._update()

    def get_path(self):
        """
        Retrieve a resource path
        """
        return self._path

    def set_x(self, x):
        """
        Set x coordinate of image (top-left)
        """
        self._x = x

    def get_x(self):
        """
        Retrieve x coordinate of image (top-left)
        """
        return self._x

    def set_y(self, y):
        """
        Set y coordinate of image (top-left)
        """
        self._y = y

    def get_y(self):
        """
        Retrieve y coordinate of image (top-left)
        """
        return self._y

    def set_width(self, width):
        """
        Set width of image
        """
        if width != self._width:
            self._width = width
            self._update()

    def get_width(self):
        """
        Retrieve width of image
        """
        return self._width

    def set_height(self, height):
        """
        Set height of image
        """
        if height != self._height:
            self._height = height
            self._update()

    def get_height(self):
        """
        Retrieve height of image
        """
        return self._height

    def _update(self):
        load_path = self._path

        if self._width > 0 and self._height > 0:
            self.bkg = Image.new('RGB', (64,64))
            self.bkg.putalpha(255)
            self._load_1 = Image.open(os.path.join(load_path, "srt_loading_1.png"))
            self._load_1.thumbnail((self._width, self._height), Image.ANTIALIAS)
            self._load_2 = Image.open(os.path.join(load_path, "srt_loading_2.png"))
            self._load_2.thumbnail((self._width, self._height), Image.ANTIALIAS)
            self._load_3 = Image.open(os.path.join(load_path, "srt_loading_3.png"))
            self._load_3.thumbnail((self._width, self._height), Image.ANTIALIAS)
            self._load_4 = Image.open(os.path.join(load_path, "srt_loading_4.png"))
            self._load_4.thumbnail((self._width, self._height), Image.ANTIALIAS)

            self._load_1_weighted = self._load_1.copy()
            self._load_2_weighted = self._load_2.copy()
            self._load_3_weighted = self._load_3.copy()
            self._load_4_weighted = self._load_4.copy()

            self._frames = []
            self._frame_num = 0

    def on_frame(self):
        """
        Handles a new frame event, for the animation
        """
        self._frame_num = (self._frame_num+1)%16

    def draw(self, canvas):
        """
        Draw the control's graphical data on the canvas.
        """
        if len(self._frames) > self._frame_num:
            composite = self._frames[self._frame_num]
        else:
            load_1_alpha = compute_alpha(alpha_min, alpha_max, (-self._frame_num)%16, 16)
            load_2_alpha = compute_alpha(alpha_min, alpha_max, (-self._frame_num+2)%16, 16)
            load_3_alpha = compute_alpha(alpha_min, alpha_max, (-self._frame_num+4)%16, 16)
            load_4_alpha = compute_alpha(alpha_min, alpha_max, (-self._frame_num+8)%16, 16)

            self.load_1_weighted.putalpha(load_1_alpha)
            self.load_2_weighted.putalpha(load_2_alpha)
            self.load_3_weighted.putalpha(load_3_alpha)
            self.load_4_weighted.putalpha(load_4_alpha)

            composite = Image.composite(self._load_1_weighted, self.bkg, self._load_1)
            composite = Image.composite(self._load_2_weighted, composite, self._load_2)
            composite = Image.composite(self._load_3_weighted, composite, self._load_3)
            composite = Image.composite(self._load_4_weighted, composite, self._load_4)
            composite = Image.alpha_composite(bkg, composite)

            self._frames += [composite.convert("RGB")]

            canvas.SetImage(composite, offset_x=self._x, offset_y=self._y)

    path = property(get_path, set_path)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    width = property(get_width, set_width)
    height = property(get_height, set_height)

