from PIL import Image
from rgbmatrix import graphics
import weakref

class Control(object):
    def __init__(self, control_id, app_base):
        self.control_id = control_id
        self.app_base = weakref.ref(app_base)
        self.z_index = 0
        self.enabled = True

    def delete(self):
        self.app_base()._delete_control(self.control_id)

    def get_static(self):
        return True

    def on_frame(self):
        return

    def draw(self, canvas):
        return

    static = property(get_static)

class TextControl(Control):
    def __init__(self, control_id, app_base):
        super(TextControl, self).__init__(control_id, app_base)
        self._font = ""
        self._font_obj = None
        self._text = ""
        self._width = 0
        self._scroll_mode = "none"
        self._color = [0, 0, 0]
        self._color_obj = graphics.Color(*self._color)
        self._x = 0
        self._y = 0
        self._align = "left"
        self._scrolling = False
        self._scroll_pos = 0
        self._scroll_dir = 0

    def set_font(self, font_name):
        if font_name != self._font:
            self._font = font_name
            self._font_obj = self.app_base().load_font(font_name)
            self._update()

    def get_font(self):
        return self._font

    def set_text(self, text):
        if text != self._text:
            self._text = text
            self._update()

    def get_text(self):
        return self._text

    def set_x(self, x):
        self._x = x

    def get_x(self):
        return self._x

    def set_y(self, y):
        self._y = y

    def get_y(self):
        return self._y

    def set_scroll(self, scroll_mode):
        self._scroll_mode = scroll_mode
        self._update_scroll()

    def get_scroll(self):
        return self._scroll_mode

    def set_align(self, align):
        self._align = align

    def get_align(self):
        return self._align

    def set_color(self, color):
        self._color = color
        self._color_obj = graphics.Color(*self._color)

    def get_color(self, color):
        return self._color

    def _update(self):
        self._width = 0
        if self._font_obj is not None:
            for character in self._text:
                self._width += self._font_obj.CharacterWidth(ord(character))
        self._update_scroll()

    def _update_scroll(self):
        self._scrolling = (self._width > self.app_base().offscreen_canvas.width and self._scroll_mode == "auto")

    def get_static(self):
        return not self._scrolling

    def on_frame(self):
        if not self._scrolling:
            return

        if self._scroll_dir == 0:
            self._scroll_pos += 1
            if self._scroll_pos >= self._width:
                self._scroll_pos = -self.app_base().offscreen_canvas.width
        else:
            self.scrolling[index]["pos"] -= 1
            if self.scrolling[index]["pos"] <= -self.app_base().offscreen_canvas.width:
                self.scrolling[index]["dir"] = self._width

    def draw(self, canvas):
        x = self._x

        if self._align == "right":
            x -= self._width
        elif self._align == "center":
            x -= self._width / 2

        x_offset = 0

        if self._scrolling:
            x = max(0, x)
            x_offset = -self._scroll_pos

        if self._font_obj is not None and self._color_obj is not None:
            graphics.DrawText(canvas, self._font_obj, x + x_offset, self._y, self._color_obj, self._text)

    font = property(get_font, set_font)
    text = property(get_text, set_text)
    scroll = property(get_scroll, set_scroll)
    color = property(get_color, set_color)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    align = property(get_align, set_align)

class ImageControl(Control):
    def __init__(self, control_id, app_base):
        super(ImageControl, self).__init__(control_id, app_base)
        self._filename = ""
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._image = None

    def set_filename(self, filename):
        if filename != self._filename:
            self._filename = filename
            self._update()

    def get_filename(self):
        return self._filename

    def set_x(self, x):
        self._x = x

    def get_x(self):
        return self._x

    def set_y(self, y):
        self._y = y

    def get_y(self):
        return self._y

    def set_width(self, width):
        if width != self._width:
            self._width = width
            self._update()

    def get_width(self):
        return self._width

    def set_height(self, height):
        if height != self._height:
            self._height = height
            self._update()

    def get_height(self):
        return self._height

    def _update(self):
        if self._filename != "" and self._width != 0 and self._height != 0:
            image = Image.open(self._filename)
            image.thumbnail((self._width, self._height), Image.ANTIALIAS)
            self._image = image.convert('RGB')

    def draw(self, canvas):
        if self._image is not None:
            canvas.SetImage(self._image, offset_x=self._x, offset_y=self._y)

    filename = property(get_filename, set_filename)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    width = property(get_width, set_width)
    height = property(get_height, set_height)

