from appbase import AppBase
from PIL import Image
from rgbmatrix import graphics
import time
import datetime

class ImageDisplay(AppBase):
    def __init__(self, *args, **kwargs):
        super(ImageDisplay, self).__init__(*args, **kwargs)

    def display_image(self, index, info, offscreen_canvas):
        if index not in self.images:
            image = Image.open(info["filename"])
            image.thumbnail((info["rect"][2], info["rect"][3]), Image.ANTIALIAS)
            self.images[index] = image.convert('RGB')

        offscreen_canvas.SetImage(self.images[index], offset_x=info["rect"][0], offset_y=info["rect"][1])

    def display_text(self, index, info, offscreen_canvas):
        if index not in self.text:
            font = self.load_font(info["font"])
            self.text[index] = {
                "font": font,
                "color": graphics.Color(*info["color"]),
                "text": info["text"],
                "width": self.get_text_width(info["text"], font)
            }

        font = self.text[index]["font"]
        textColor = self.text[index]["color"]
        if info["text"] == self.text[index]["text"]:
            textWidth = self.text[index]["width"]
        else:
            textWidth = self.get_text_width(info["text"], font)

        x = info["point"][0]
        y = info["point"][1]

        if info["align"] == "right":
            x -= textWidth
        elif info["align"] == "center":
            x -= textWidth / 2

        x_offset = 0

        if textWidth > offscreen_canvas.width:
            if info["scroll"] == "auto":
                x = max(0, x)

                if index not in self.scrolling:
                    self.staticDisplay = False
                    self.scrolling[index] = {
                        "pos": 0,
                        "dir": 0
                    }

                x_offset = -self.scrolling[index]["pos"]

                if self.scrolling[index]["dir"] == 0:
                    self.scrolling[index]["pos"] += 1
                    if self.scrolling[index]["pos"] >= textWidth:
                        self.scrolling[index]["pos"] = -offscreen_canvas.width
                else:
                    self.scrolling[index]["pos"] -= 1
                    if self.scrolling[index]["pos"] <= -offscreen_canvas.width:
                        self.scrolling[index]["dir"] = textWidth

        graphics.DrawText(offscreen_canvas, font, x + x_offset, y, textColor, info["text"])

    def run(self):
        self.staticDisplay = True
        self.images = {}
        self.text = {}
        self.scrolling = {}

        self.matrix.Clear()
        offscreen_canvas = self.matrix.CreateFrameCanvas()

        while not self.stopFlag:
            offscreen_canvas.Clear()
            for i,display in enumerate(self.app_config["display"]):
                if display["type"] == "image":
                    self.display_image(i, display, offscreen_canvas)

                elif display["type"] == "text":
                    self.display_text(i, display, offscreen_canvas)

                elif display["type"] == "datetime":
                    self.staticDisplay = False
                    time_val = datetime.datetime.now()
                    text_display = dict(display)
                    text_display["text"] = time_val.strftime(display["format"])
                    self.display_text(i, text_display, offscreen_canvas)

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

            if self.staticDisplay:
                break

            time.sleep(0.1)
