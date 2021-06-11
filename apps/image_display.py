from appbase import AppBase
from PIL import Image
from rgbmatrix import graphics
import time
import datetime

class ImageDisplay(AppBase):
    def __init__(self, *args, **kwargs):
        super(ImageDisplay, self).__init__(*args, **kwargs)

    def run(self):
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

            elif display["type"] == "text":
                text_control = self.create_control("text", "text_" + str(i))
                text_control.font = display["font"]
                text_control.color = display["color"]
                text_control.text = display["text"]
                text_control.x = display["point"][0]
                text_control.y = display["point"][1]
                text_control.align = display["align"]
                text_control.scroll = display["scroll"]
                if not text_control.static:
                    static_display = False

            elif display["type"] == "datetime":
                text_control = self.create_control("text", "text_" + str(i))
                text_control.font = display["font"]
                text_control.color = display["color"]
                text_control.x = display["point"][0]
                text_control.y = display["point"][1]
                text_control.align = display["align"]
                text_control.scroll = display["scroll"]

                clocks += [{
                    "format": display["format"],
                    "control": text_control
                }]

                static_display = False

        while not self.stopFlag:
            time_val = datetime.datetime.now()
            for clock in clocks:
                clock["control"].text = time_val.strftime(clock["format"])

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

            if static_display:
                break

            time.sleep(0.1)
