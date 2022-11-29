
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy import platform
from kivy.core.window import Window
from kivy.config import Config
Config.set('graphics', 'width', 900)
Config.set('graphics', 'height', 400)


class MainWidget(Widget):
    from transform import transform_perspective, transform_2D, transform
    from user_actions import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 10
    V_LINES_SPACING = .25
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = .1
    horizontal_lines = []

    current_offset_y = 0
    SPEED_Y = 3
    current_offset_x = 0
    SPEED_X = H_LINES_SPACING*100
    current_speed_x = 0   # SPEED

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_line()
        self.init_horizontal_line()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(
                self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        pass

    def on_perspective_point_x(self, widget, value):
        pass

    def on_perspective_point_y(self, widget, value):
        pass

    def init_vertical_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line(size=5))

    def update_vertical_lines(self):
        center_line_x = int(self.width/2)
        offset = -int(self.V_NB_LINES/2)+0.5
        spacing = self.V_LINES_SPACING * self.width
        # self.line.points = [center_x, 0, center_x, 100]
        for i in range(self.V_NB_LINES):
            line_x = center_line_x + offset * spacing + self.current_offset_x
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]
            offset += 1

    def init_horizontal_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        center_line_x = int(self.width/2)
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES/2)+0.5

        x_min = center_line_x + offset*spacing + self.current_offset_x
        x_max = center_line_x - offset*spacing + self.current_offset_x

        spacing_y = self.H_LINES_SPACING*self.height

        for i in range(0, self.H_NB_LINES):
            line_y = i * spacing_y - self.current_offset_y
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        self.update_vertical_lines()
        self.update_horizontal_lines()

        time_factor = dt*60
        self.current_offset_y += self.SPEED_Y*time_factor
        self.current_offset_x += self.current_speed_x*time_factor

        spacing_y = self.H_LINES_SPACING*self.height
        if self.current_offset_y > spacing_y:
            self.current_offset_y -= spacing_y


class GalaxyApp(App):
    pass


GalaxyApp().run()
