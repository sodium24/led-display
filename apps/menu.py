from appbase import AppBase
import time
import datetime
import threading

class Menu(AppBase):
    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

        self.menu_row = 0
        self.selected_app = None
        self.current_screen_name = None

        self.menu_items = []
        self.menu_title = None
        self.menu_selection = None
        self.menu_controls = []

        for entry_info in self.app_config["menu"]:
            self.menu_items += [(entry_info["text"], entry_info["screen"])]

        self.redraw_lock = threading.Lock()

    def stop(self):
        super(Menu, self).stop()

        # Pass on the signal to a running app
        if self.running_app is not None:
            self.running_app.stop()

    def on_input_event(self, input_event):
        handled = False

        if not handled and self.running_app is not None:
            handled = self.running_app.on_input_event(input_event)

        if not handled and self.running_app is None:
            if input_event == "up":
                self.menu_row -= 1
                self.menu_row %= len(self.menu_items)
                self.redraw()
                handled = True
            elif input_event == "down":
                self.menu_row += 1
                self.menu_row %= len(self.menu_items)
                self.redraw()
                handled = True
            elif input_event == "select":
                self.selected_app = self.menu_row
                handled = True

        return handled

    def redraw(self):
        with self.redraw_lock:
            selected_row = self.menu_row

            # Update the menu selection position
            self.menu_selection.y = self.menu_controls[selected_row].y + 1 - self.menu_selection.height

            # Update the selected color
            for menu_item in self.menu_controls:
                menu_item.color = self.app_config["item_color"]

            self.menu_controls[selected_row].color = self.app_config["selected_fgcolor"]

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

    def _start_app(self, index):
        self.selected_app = index
        screen_name = self.menu_items[self.selected_app][1]
        self.current_screen_name = screen_name
        self._start_app_by_name(screen_name)

    def run(self):
        y = 0

        menu_title = self.create_control("text", "menu_title")
        menu_title.font = self.app_config["title_font"]
        menu_title.color = self.app_config["title_color"]
        menu_title.text = self.app_config["title_text"]
        menu_title.x = self.offscreen_canvas.width / 2
        menu_title.y = y + self.app_config["title_height"]
        menu_title.align = "center"
        menu_title.scroll = "auto"
        menu_title.enabled = True

        y += menu_title.y

        menu_selection = self.create_control("rect", "menu_selection")
        menu_selection.x = 0
        menu_selection.y = y + 2
        menu_selection.width = self.offscreen_canvas.width
        menu_selection.height = self.app_config["item_height"] - 1
        menu_selection.has_stroke = False
        menu_selection.has_fill = True
        menu_selection.fill_color = self.app_config["selected_bgcolor"]

        self.menu_title = menu_title
        self.menu_selection = menu_selection

        menu_controls = []

        for i,item in enumerate(self.menu_items):
            menu_item = self.create_control("text", "menu_item_" + str(i))
            menu_item.font = self.app_config["item_font"]
            menu_item.color = self.app_config["item_color"]
            menu_item.text = item[0]
            menu_item.x = 0
            menu_item.y = y + self.app_config["item_height"]
            menu_item.align = "left"
            menu_item.scroll = "auto"
            menu_item.enabled = True

            self.menu_controls += [menu_item]

            y += self.app_config["item_height"]

        self.redraw()

        is_static = self.is_static()

        while not self.stop_flag:
            if self.selected_app is not None:
                try:
                    self._start_app(self.selected_app)
                    self.selected_app = None
                except Exception as err:
                    print("Exception while running app: %s" % err)
                    self.selected_app = None
                    self.running_app = None
            else:
                if is_static:
                    time.sleep(1)
                else:
                    self.redraw()
                    time.sleep(0.1)
