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
        super(LoadScreen, self).__init__(*args, **kwargs)

    def run(self):
        """
        Load configuration and display the load screen
        """
        load_path = self.app_config["path"]

        bkg = Image.new('RGB', (64,64))
        bkg.putalpha(255)

        load_1 = Image.open(os.path.join(load_path, "srt_loading_1.png"))
        load_2 = Image.open(os.path.join(load_path, "srt_loading_2.png"))
        load_3 = Image.open(os.path.join(load_path, "srt_loading_3.png"))
        load_4 = Image.open(os.path.join(load_path, "srt_loading_4.png"))

        load_1_weighted = load_1.copy()
        load_2_weighted = load_2.copy()
        load_3_weighted = load_3.copy()
        load_4_weighted = load_4.copy()

        alpha_min = 75
        alpha_max = 205

        frames = []

        # generate frames with different alpha values
        for frame_num in range(40):
            load_1_alpha = compute_alpha(alpha_min, alpha_max, (-frame_num)%40, 40)
            load_2_alpha = compute_alpha(alpha_min, alpha_max, (-frame_num+5)%40, 40)
            load_3_alpha = compute_alpha(alpha_min, alpha_max, (-frame_num+10)%40, 40)
            load_4_alpha = compute_alpha(alpha_min, alpha_max, (-frame_num+15)%40, 40)

            load_1_weighted.putalpha(load_1_alpha)
            load_2_weighted.putalpha(load_2_alpha)
            load_3_weighted.putalpha(load_3_alpha)
            load_4_weighted.putalpha(load_4_alpha)

            composite = Image.composite(load_1_weighted, bkg, load_1)
            composite = Image.composite(load_2_weighted, composite, load_2)
            composite = Image.composite(load_3_weighted, composite, load_3)
            composite = Image.composite(load_4_weighted, composite, load_4)
            composite = Image.alpha_composite(bkg, composite)

            frames += [composite.convert("RGB")]

        i = 0
        while not self.stop_event.wait(0.05):
            self.offscreen_canvas.SetImage(frames[i])
            i = (i+1)%len(frames)

            # redraw the display
            self.draw()


