################################################################################
# image_display.py
#-------------------------------------------------------------------------------
# Customizable app for showing images, text, clock, etc on the LED display.
# Its operation can be adjusted through the JSON configuration settings.
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

from ..app_base import AppBase

class ImageDisplay(AppBase):
    """
    Customizable app to display images, text, clock, etc
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the app
        """
        super(ImageDisplay, self).__init__(*args, **kwargs)

    def run(self):
        """
        Load configuration and display the result
        """
        static_display = True
        clocks = []

        for i,display in enumerate(self.app_config["display"]):
            if display["type"] == "image":
                image_control = self.create_control("image", "image_" + str(i))
                image_control.filename = display["filename"]
                image_control.x = display["rect"][0]
                image_control.y = display["rect"][1]
                image_control.width = display["rect"][2]
                image_control.height = display["rect"][3]
                image_control.enabled = display.get("enable", True)

            elif display["type"] == "text":
                text_control = self.create_control("text", "text_" + str(i))
                text_control.font = display["font"]
                text_control.color = display["color"]
                text_control.text = display["text"]
                text_control.x = display["point"][0]
                text_control.y = display["point"][1]
                text_control.align = display["align"]
                text_control.scroll = display["scroll"]
                text_control.enabled = display.get("enable", True)
                if text_control.enabled and not text_control.static:
                    static_display = False

            elif display["type"] == "datetime":
                text_control = self.create_control("text", "text_" + str(i))
                text_control.font = display["font"]
                text_control.color = display["color"]
                text_control.x = display["point"][0]
                text_control.y = display["point"][1]
                text_control.align = display["align"]
                text_control.scroll = display["scroll"]
                text_control.enabled = display.get("enable", True)

                clocks += [{
                    "format": display["format"],
                    "control": text_control
                }]

                if text_control.enabled:
                    static_display = False

        while not self.stop_event.wait(0.1):
            # update the time on any clocks
            time_val = datetime.datetime.now()
            for clock in clocks:
                clock["control"].text = time_val.strftime(clock["format"])

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

            if static_display:
                break

        self.stop_event.wait()
