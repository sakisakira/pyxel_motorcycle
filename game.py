import pyxel
import random
from color_palette import *
from world import *
from physics import *
from stages import *
from background import *
from input import *
from face import *
from status import *
from title import *
from result import *
from sound import *
from music import *

class CharaBodyIndex(Enum):
    Normal = auto()
    Succeeded = auto()

class GameState(Enum):
    GameTitle = auto()
    GamePlay = auto()
    GameResult = auto()

class GameBike:
    def __init__(self, image_index, path):
        self.bike = Bike()
        self.width = BikeSpriteWidth
        self.height = BikeSpriteHeight
        self.image_index = image_index
        self.next_blink_tic = 20
        self.chara_body_index = CharaBodyIndex.Normal
        self.load(path)
        self.set_sprite_ranges()
        

    def load(self, path):
        self.image = pyxel.images[self.image_index]
        self.image.load(0, 0, path)

    def set_sprite_ranges(self):
        w = BikeSpriteWidth
        h = BikeSpriteHeight
        self.bike_body_range = Range2(0, 0, w, h)
        self.chara_body_range_0 = Range2(w, 0, w, h)
        self.chara_body_range_1 = Range2(w, h, w, h)
        self.chara_body_range_steer = Range2(w, h * 2, w, h)
        r = BikeSpriteHeight / 4
        self.tire_range = Range2(w * 2, 0, r * 2, r * 2)
        self.front_tire_center = Vec2(w / 2 - r, r)
        self.rear_tire_center = Vec2(-w / 2 + r, r)

    def screen_xy(self):
        w_loc = self.bike.location
        s_loc = world.screen_xy(w_loc)
        return Vec2(s_loc.x - self.width / 2,
                    s_loc.y - self.height / 2)

    def rotation_degree(self):
        rotation = self.bike.rotation
        return 180.0 / math.pi * rotation

    def tire_rotation_degree(self):
        r = BikeWorldLen / 6
        l = math.pi * 2 * r
        ratio = (self.bike.location.x % l) / l
        return -180.0 * ratio

    def chara_body_range(self):
        if self.chara_body_index == CharaBodyIndex.Succeeded:
            return self.chara_body_range_steer
        if self.bike.rotation_velocity < 0:
            return self.chara_body_range_0
        else:
            return self.chara_body_range_1
        
    def show(self):
        s_xy = self.screen_xy()
        rot = self.rotation_degree()
        r = self.tire_range
        f_rel = self.front_tire_center.rotate(-self.bike.rotation)
        f_xy = s_xy + f_rel + self.front_tire_center
        tire_rot = self.tire_rotation_degree()
        pyxel.blt(f_xy.x, f_xy.y, self.image_index,
                  r.x, r.y, r.w, r.h,
                  world.bg_index,
                  tire_rot)
        r_rel = self.rear_tire_center.rotate(-self.bike.rotation)
        r_xy = s_xy + r_rel + self.front_tire_center
        pyxel.blt(r_xy.x, r_xy.y, self.image_index,
                  r.x, r.y, r.w, r.h,
                  world.bg_index,
                  tire_rot)
        r = self.bike_body_range
        pyxel.blt(s_xy.x, s_xy.y, self.image_index,
                  r.x, r.y, r.w, r.h,
                  world.bg_index,
                  rot)
        r = self.chara_body_range()
        pyxel.blt(s_xy.x, s_xy.y, self.image_index,
                  r.x, r.y, r.w, r.h,
                  world.bg_index,
                  rot)
        
    def update(self, ground, btn_a, btn_b):
        self.bike.update(ground, btn_a, btn_b)
        self.chara_body_index = CharaBodyIndex.Normal

    def update_chara_body_index(self, index):
        self.chara_body_index = index

    def failed(self):
        return self.bike.failed()

    def face_index(self):
        if abs(math.sin(self.bike.rotation)) > 0.65:
            return FaceIndex.Astonish
        if world.tic % self.next_blink_tic == 0:
            return FaceIndex.Blink
        elif world.tic % self.next_blink_tic == 1:
            self.next_blink_tic = random.randint(10, 30)
            return FaceIndex.Blink
        else:
            return FaceIndex.Normal

class GameGround:
    def ground(self):
        return stages[world.stage_index].ground

    def screen_y(self, screen_x):
        w_xy = world.world_xy(Vec2(screen_x, 0))
        w_y = self.ground().height(w_xy.x)
        if not w_y: return False
        s_xy = world.screen_xy(Vec2(w_xy.x, w_y))
        return s_xy.y

    def color_index(self, screen_x):
        w_x = world.world_xy(Vec2(screen_x, 0)).x
        x = int(w_x) % 10
        if x < 5:
            return ColorPalette.Ground0
        else:
            return ColorPalette.Ground1

    def show(self):
        for x in range(world.screen_size.x):
            y = self.screen_y(x)
            if not y: continue
            col = self.color_index(x)
            pyxel.line(x, y, x, world.screen_size.y, col)

class App:
    BikesImagePath = 'images/bike.png'
    FacesImagePath = 'images/faces.png'
    TitleImagePath = 'images/title.png'
    
    def __init__(self):
        pyxel.init(world.screen_size.x,
                   world.screen_size.y,
                   world.title)
        self.color_palette = ColorPalette(
            [self.BikesImagePath,
             self.FacesImagePath,
             self.TitleImagePath])
        self.state = GameState.GameTitle
        self.title = Title(image_index = 2, path = self.TitleImagePath)
        self.bike = GameBike(image_index = 0, path = self.BikesImagePath)
        self.ground = GameGround()
        world.start()
        self.input = Input()
        self.face = Face(image_index = 1, path = self.FacesImagePath)
        self.status = Status()
        self.result = Result()
        self.sound = Sound(sound_index = 0)
        self.music = Music(sound_index = 1)
        self.reset()
        pyxel.run(self.update, self.draw)

    def stage(self):
        return stages[world.stage_index]

    def bike_x_diff(self):
        diff_max = world.origin_screen.x
        v_max = self.bike.bike.max_speed
        v = self.bike.bike.velocity.x
        return v / v_max * diff_max / world.scale.x

    def goal_distance(self):
        return self.stage().ground.goal_x() - self.bike.bike.location.x

    def update_face(self, in_game, succeeded):
        if in_game:
            self.face.update(self.bike.face_index())
        else:
            if succeeded:
                self.face.update(FaceIndex.Smile)
            else:
                self.face.update(FaceIndex.Cry)

    def update_in_game(self):
        self.background.update(world.origin_world.x)
        bike = self.bike.bike
        ox = bike.location.x + self.bike_x_diff()
        world.update(Vec2(ox, 0))
        self.input.update(True)
        btn_a = self.input.a_pressed
        btn_b = self.input.b_pressed
        self.bike.update(self.stage().ground, btn_a, btn_b)
        self.status.update(self.bike.bike, self.stage().ground)
        self.update_face(True, False)
        self.result.update(False, False)
        if self.input.reset_pressed:
            self.reset()

    def update_result(self, failed, result_time):
        self.input.update(False)
        self.bike.update_chara_body_index(CharaBodyIndex.Succeeded)
        self.result.update(failed, result_time)
        self.update_face(False, not failed)
        if self.input.x_pressed:
            if result_time:
                stages[world.stage_index].update_best_time(result_time)
                s_i = (world.stage_index + 1) % len(stages)
                world.stage_index = s_i
            self.reset()

    def update(self):
        if self.state == GameState.GameTitle:
            self.title.update()
            if self.title.pressed():
                self.reset()
                self.state = GameState.GamePlay
        elif self.state == GameState.GamePlay:
            failed = self.bike.failed()
            if self.goal_distance() <= 0:
                result_time = world.elapsed_time
            else:
                result_time = False
                if failed or result_time:
                    self.music.stop()
                    self.update_result(failed, result_time)
                    self.sound.update(False)
                else:
                    self.update_in_game()
                    self.sound.update(self.bike.bike.speed_ratio())
        elif self.state == GameState.GameResult:
            pass
        else:
            raise

    def draw(self):
        if self.state == GameState.GameTitle:
            self.title.show()
        elif self.state == GameState.GamePlay:
            self.background.show()
            self.bike.show()
            self.ground.show()
            self.input.show()
            self.face.show()
            self.status.show()
            self.result.show()
        elif self.state == GameState.GameResult:
            pass
        else:
            raise

    def reset(self):
        world.start()
        self.background = Background()
        self.bike.bike.reset()
        self.music.play()

App()
