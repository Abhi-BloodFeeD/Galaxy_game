
import random
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy import platform
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.config import Config
Config.set('graphics', 'width', 1200)
Config.set('graphics', 'height', 900)


Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transform import transform_perspective, transform_2D, transform
    from user_actions import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed

    menu_widget = ObjectProperty()
    menu_title = StringProperty("G   A   L   A    X    Y")
    menu_button_title = StringProperty("P l a y")
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    score_txt = StringProperty("")
    V_NB_LINES = 5
    V_LINES_SPACING = .25
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = .1
    horizontal_lines = []

    current_offset_y = 0
    # SCREEN_SIZE_FACTOR = 0
    current_y_loop = 0
    SPEED_Y = 0.004
    current_offset_x = 0
    SPEED_X = 15*H_LINES_SPACING/100
    current_speed_x = 0   # SPEED

    NB_TILES = 22
    tiles = []
    tiles_coordinates = []

    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]
    SHIP_WIDTH = .04
    SHIP_HEIGHT = .035
    SHIP_BASE_Y = 0.04

    state_game_over = False
    state_game_has_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tile_coordinate()
        self.generate_tiles_coordinates()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(
                self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load(
            "audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load(
            "audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .15
        self.sound_galaxy.volume = .15
        self.sound_gameover_impact.volume = .4
        self.sound_gameover_voice.volume = .15
        self.sound_restart.volume = .15

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.menu_title = "GAME OVER !"
        self.menu_button_title = "R e s t a r t"
        self.score_txt = "SCORE : " + str(self.current_y_loop)
        self.SPEED_Y = 0.004
        self.tiles_coordinates = []
        self.pre_fill_tile_coordinate()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_vertical_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line(size=5))

    def init_tiles(self):
        with self.canvas:
            for i in range(self.NB_TILES):
                Color(1, 1, 1)
                self.tiles.append(Quad())

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)

            start_index = -int(self.V_NB_LINES/2)+1
            end_index = start_index + self.V_NB_LINES - 2    # NOT SAME

            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))

            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def pre_fill_tile_coordinate(self):
        for i in range(20):
            self.tiles_coordinates.append((0, i))

    def get_line_x_from_index(self, index):
        center_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index-0.5
        line_x = center_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self. current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)

        return x, y

    def update_tiles(self):
        for i in range(self.NB_TILES):
            tile = self.tiles[i]
            tiles_x, tiles_y = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tiles_x, tiles_y)
            xmax, ymax = self.get_tile_coordinates(tiles_x+1, tiles_y+1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2) + 1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES/2) + 1
        end_index = start_index+self.V_NB_LINES - 1
        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        time_factor = dt*60
        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED_Y*self.height
            self.current_offset_y += speed_y*time_factor
            spacing_y = self.H_LINES_SPACING*self.height
            while self.current_offset_y > spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE : " + str(self.current_y_loop)
                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width
            self.current_offset_x += speed_x*time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 1)
            print(f"GAME OVER")

    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def check_ship_collision(self):
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)

        for i in range(3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(1, 0, 1)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH*self.width
        ship_height = self.height*self.SHIP_HEIGHT
        x1 = center_x-ship_half_width
        y1 = base_y
        x2 = center_x+ship_half_width
        y2 = base_y
        x3 = center_x
        y3 = base_y+ship_height

        self.ship_coordinates[0] = (x1, y1)
        self.ship_coordinates[1] = (x2, y2)
        self.ship_coordinates[2] = (x3, y3)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()
