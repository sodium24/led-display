from appbase import AppBase

class DisplayOff(AppBase):
    def __init__(self, *args, **kwargs):
        super(DisplayOff, self).__init__(*args, **kwargs)

    def run(self):
        self.matrix.Clear()
        self.enter_sleep_mode()
