import pyxel
from color_palette import *
from world import *
from physics import *
from stages import *
from background import *
from input import *
from face import *
from status import *

class GameBike:
    def __init__(self, image_index):
        self.bike = Bike()
        self.width = BikeSpriteWidth
        self.height = BikeSpriteHeight
        self.wheel_radius = 8
        self.front_wheel_center = Vec2(12, 8)
        self.rear_wheel_center = Vec2(8, 8)
        self.image_index = image_index
        self.load()

    def load(self):
        self.image = pyxel.images[self.image_index]
        self.image.load(0, 0, "images/bike.png")

    def screen_xy(self):
        w_loc = self.bike.get_location()
        s_loc = world.screen_xy(w_loc)
        return Vec2(s_loc.x - self.width / 2,
                    s_loc.y - self.height / 2)

    def rotation_degree(self):
        rotation = self.bike.rotation
        return 180.0 / math.pi * rotation
        
    def show(self):
        s_xy = self.screen_xy()
        rot = self.rotation_degree()
        pyxel.blt(s_xy.x, s_xy.y, self.image_index,
                  0, 0, self.width, self.height,
                  world.bg_index,
                  rot)
        
    def update(self, ground, btn_a, btn_b):
        self.bike.update(ground.ground, btn_a, btn_b)

class GameGround:
    ColorIndex0 = 9
    ColorIndex1 = 10
    
    def __init__(self):
        self.ground = stages[0].ground
        self.color0 = 1
        self.color1 = 2

    def screen_y(self, screen_x):
        w_xy = world.world_xy(Vec2(screen_x, 0))
        w_y = self.ground.height(w_xy.x)
        if not w_y: return False
        s_xy = world.screen_xy(Vec2(w_xy.x, w_y))
        return s_xy.y

    def color_index(self, screen_x):
        w_x = world.world_xy(Vec2(screen_x, 0)).x
        x = int(w_x) % 10
        if x < 5:
            return self.ColorIndex0
        else:
            return self.ColorIndex1

    def show(self):
        for x in range(world.screen_size.x):
            y = self.screen_y(x)
            if not y: continue
            col = self.color_index(x)
            pyxel.line(x, y, x, world.screen_size.y, col)

class App:
    def __init__(self):
        pyxel.init(world.screen_size.x,
                   world.screen_size.y,
                   world.title)
        self.color_palette = ColorPalette()
        self.background = Background()
        self.bike = GameBike(0)
        self.ground = GameGround()
        world.start()
        self.input = Input()
        self.face = Face(1)
        self.status = Status()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.background.color_index = self.color_palette.sky
        bike = self.bike.bike
        ox = bike.location.x + bike.velocity.x * 0.2
        world.update(Vec2(ox, 0))
        self.input.update()
        btn_a = self.input.a_pressed
        btn_b = self.input.b_pressed
        self.bike.update(self.ground, btn_a, btn_b)
        self.status.update(self.bike.bike, self.ground.ground)

    def draw(self):
        self.background.show()
        self.bike.show()
        self.ground.show()
        self.input.show()
        self.face.show()
        self.status.show()

App()
