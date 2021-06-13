################################################################################
# slideshow.py
#-------------------------------------------------------------------------------
# An app to display a collection of pictures from specified folder(s) on the
# LED display.
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

import time
import datetime
import os
from app_base import AppBase

class Slideshow(AppBase):
    """
    App to display a collection of pictures
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the app
        """
        super(Slideshow, self).__init__(*args, **kwargs)

    def run(self):
        """
        Main routine to load pictures from folders based on the app configuration,
        and display them in sequence on the LED display
        """
        files = []
        image_controls = []
        for folder in self.app_config["folders"]:
            for filename in os.listdir(folder):
                if os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                    files += [os.path.join(folder, filename)]

        for i,filename in enumerate(files):
            image_control = self.create_control("image", "image_" + str(i))
            image_control.filename = filename
            image_control.x = 0
            image_control.y = 0
            image_control.width = self.offscreen_canvas.width
            image_control.height = self.offscreen_canvas.height
            image_control.enabled = False
            image_controls += [image_control]

        current_indx = 0

        while len(image_controls) > 0 and not self.stop_event.is_set():
            image_controls[current_indx].enabled = True

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

            # display for a delay
            if self.stop_event.wait(self.app_config["delay"]):
                break

            # go on to the next picture
            image_controls[current_indx].enabled = False

            current_indx += 1
            current_indx %= len(image_controls)
