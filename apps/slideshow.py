from appbase import AppBase
import time
import datetime
import os

class Slideshow(AppBase):
    def __init__(self, *args, **kwargs):
        super(Slideshow, self).__init__(*args, **kwargs)

    def run(self):
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

        while len(image_controls) > 0 and not self.stopFlag:
            image_controls[current_indx].enabled = True

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

            for n in range(5):
                if self.stopFlag: break
                time.sleep(1)

            image_controls[current_indx].enabled = False

            current_indx += 1
            if current_indx >= len(image_controls):
                current_indx = 0
