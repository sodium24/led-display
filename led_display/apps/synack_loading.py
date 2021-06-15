from PIL import Image

from ..app_base import AppBase
import os

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

class SynackLoading(AppBase):
    """
    Cool Synack load screen
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the app
        """
        super(SynackLoading, self).__init__(*args, **kwargs)

    def run(self):
        """
        Load configuration and display the load screen
        """
        load_path = self.app_config["path"]

        load_control = self.create_control("synack_load", "synackLoadControl")
        load_control.path = load_path
        load_control.x = 0
        load_control.y = 0
        load_control.width = 64
        load_control.height = 64

        while not self.stop_event.wait(0.1):

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()



