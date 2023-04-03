from typing import Optional
import pyglet.shapes as shapes
from pyglet.graphics import Batch
from pyglet.window import key, mouse

import pymunk
from pymunk import Vec2d as Vec

from .animation import *
from .notation import _Label, _Message, _DynamicLabel

mv_keys = [key.A, key.LEFT, key.D, key.RIGHT, key.UP, key.W, key.DOWN, key.S]
L = mv_keys[:2]
R = mv_keys[1:4]
U = mv_keys[3:6]
D = [key.DOWN, key.S]
DIRS = [Vec(0, -1), Vec(1, 0), Vec(0, 1), Vec(-1, 0)]

DAY_LENGTH = 24 * 3600
HOUR_LENGTH = 3600
MINUTE_LENGTH = 60

LB = 453.59
OZ = 28.35
G = 1

CAN_WEIGHT = OZ * .5
BOTTLE_WEIGHT = 23 * G
GLASS_WEIGHT = LB

CAN_PRICE = 1.66
BOTTLE_PRICE = 1.33
GLASS_PRICE = 0.10

containers = ["cans", "bottles", "glass"]

def calculate_weight(item: str, amount: int):
    if item == "cans":
        return round((amount * CAN_WEIGHT) / LB, 2)
    elif item == "bottles":
        return round((amount * BOTTLE_WEIGHT) / LB, 2)
    elif item == "glass":
        return round((amount * GLASS_WEIGHT) / LB, 2)

def calculate_cans_weight(amount: int):
    return calculate_weight("cans", amount)

def calculate_bottles_weight(amount: int):
    return calculate_weight("bottles", amount)

def calculate_glass_weight(amount: int):
    return calculate_weight("glass", amount)

def calculate_value(item: str, weight: int):
    if item == "cans":
        return weight * CAN_PRICE
    if item == "bottles":
        return weight * BOTTLE_PRICE
    if item == "glass":
        return weight * GLASS_PRICE
    
def calculate_cans_value(weight: int):
    return calculate_value("cans", weight)

def calculate_bottles_value(weight: int):
    return calculate_value("bottles", weight)

def calculate_glass_value(weight: int):
    return calculate_value("glass", weight)


def cpfclamp(f, min_, max_):
    """Clamp f between min and max
    :param f:
    :param min_:
    :param max_:
    :return:
    """
    return min(max(f, min_), max_)


class AbstractPlayer:
    """Abstract class for a player type that has no visual representation. Instead, this class is used to create a
    player that can be used as a container of specific attributes related to differing game models, such as an
    idle-RPG, a tycoon game, a text-based rpg, etc."""
    DEFAULT_ATTRIBUTES = {
        "playtime": "00:00:00:00",
        "gametime": "00:00:00:00",
    }

    def __init__(
            self,
            main_window,
            scene
    ):
        self.window = main_window
        self.scene = scene
        self.clock = self.window.clock
        self.__dict__.update(AbstractPlayer.DEFAULT_ATTRIBUTES)
        self.in_game_hours = self.scene.gametime.in_game_hours
        self.labels = []
        self.event_labels = []
        self.create_labels()


    def create_labels(self):
        for attr in self.__dict__.keys():
            keys_len = len(list(self.__dict__.keys()))
            if attr.startswith("_") or attr.startswith("auto") or attr.startswith("rate") or attr.startswith(
                    "degree") or attr.startswith("total") or attr in ["window", "scene", "clock", "labels",
                                                                      "carry_limit", "stockpile_limit",
                                                                      "event_labels"] or attr is None:
                continue
            self.labels.append(
                _DynamicLabel(
                    parent=self,
                    attr=str(attr),
                    x= 50,
                    y= 1080 - 100 - (len(self.labels) * 20),
                )
            )

    def add_event_label(self, event_message, duration=20, row=None):
        row = row if row is not None else len(self.event_labels)
        r = row * 20
        with _Message.context(self, 900, 1080 - 100 - r, event_message, None, duration) as msg:
            self.event_labels.append(msg)

    def refresh_labels(self):
        [label.update() for label in self.labels]
        [label.update() for label in self.event_labels]

    def draw_labels(self):
        [label.draw() for label in self.labels]
        [label.draw() for label in self.event_labels]



    def restore_(
            self,
            var: Optional[str] = None,
            amount: Optional[int] = 1
    ):
        self.__setattr__(var, self.__getattribute__(var) + amount)
        if self.__getattribute__(var).__gt__(100):
            self.__setattr__(var, 100)

    def restore_energy(
            self,
            amount: Optional[float] = None
    ):
        if self.energy < 100:
            self.restore_(
                var="energy",
                amount=amount if amount is not None else 1)
        else:
            print("Energy is full!")

    def restore_health(
            self,
            amount: Optional[float] = None
    ):
        if self.health < 100:
            self.restore_(
                var="health",
                amount=amount if amount is not None else 1
            )

    def check_level(self):
        if self.xp >= self.level * 100:
            return True

    def update(self):
        self.playtime = self.scene.realtime
        self.gametime = self.scene.ingame
        self.in_game_hours = self.scene.gametime.in_game_hours
        self.refresh_labels()

    def draw(self):
        self.draw_labels()




class Player:
    def __init__(self, main_window, scene, x: Optional[int], y: Optional[int], offset: Optional[tuple],
                 size: Optional[tuple], visual: Optional[str], *args, **kwargs):
        self._contact_points = None
        self.name = str(self.__class__.__name__)
        print(f"Introducing new player[{self.name}]")
        self.window = main_window
        self.scene = scene
        self.debug_batch = Batch()
        self.world = scene.world
        print(f"Path: {self.path}")
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.position = (self.x, self.y)
        self.offset = offset if offset is not None else (0, 0)
        self.age = 0
        self.moving = False
        self.action = 0
        self.facing = 0
        self.dead = False
        self.size = size if size is not None else (0, 0)
        self.speed = 0
        self.jump_str = 0
        self.body = pymunk.Body(10, 1, pymunk.Body.DYNAMIC)
        self.body.position = (x + self.offset[0], y + self.offset[1])
        self.poly = pymunk.Poly.create_box(self.body, self.size)
        self.poly.friction = .5
        self.poly.elasticity = 0
        self.world.add(self.body, self.poly)
        self.velocity = self.body.velocity
        self._outline_points = self.sort_points
        self._outlines = self.build_border()
        self.debug_labels = []
        #        self.create_debug_labels()
        self.flip = 1
        self.animation = None
        self.visual = visual if visual is not None else "default"
        self.get_visual()
        self.state_frame = None

    def create_debug_labels(self):
        self.debug_labels.append(_DynamicLabel(self, "x", 1920 - 100, 1080 - 100))
        self.debug_labels.append(_DynamicLabel(self, "y", 1920 - 100, 1080 - 110))
        self.debug_labels.append(_DynamicLabel(self, "speed", 1920 - 100, 1080 - 130))
        self.debug_labels.append(_DynamicLabel(self, "grounded", 1920 - 100, 1080 - 140))
        self.debug_labels.append(_DynamicLabel(self, "moving", 1920 - 100, 1080 - 150))
        self.debug_labels.append(_DynamicLabel(self, "jumping", 1920 - 100, 1080 - 160))
        self.debug_labels.append(_DynamicLabel(self, "facing", 1920 - 100, 1080 - 170))
        self.debug_labels.append(_DynamicLabel(self, "velocity", 1920 - 150, 1080 - 180))

    def get_visual(self):
        if self.visual == "default":
            self.load_animation()
        elif self.visual == "shape":
            self.load_shape()

    def load_shape(self):
        s = shapes.Rectangle(self.x, self.y, self.size[0], self.size[1], color=(255, 255, 255))
        self.__setattr__("shape", s)

    def load_animation(self):
        animas = [PPlayerAnim(self), APlayerAnim(self), AHeroAnim(self), NewPlayerAnim(self), HorseAnim(self)]
        print("Loading animation ...")
        for anim in animas:
            if self.name == anim.__class__.__name__.replace("Anim", ""):
                print(f"Found animation for {self.name}")
                self.__setattr__("animation", anim)
                self.animation.init()
                self.__setattr__("state_frame", self.animation.state.frame_)
                print(f"Prepared {self.name} animation ...")
                break
        else:
            print("Animation not found ...")

    @property
    def sort_points(self):
        """ Arrange the vertices of the bounding box, return a list of coordinates."""
        lines = []
        for line in self.get_points():
            start_end = []
            for point in line:
                x, y = point[0], point[1]
                start_end.extend((x, y))
            line = start_end[0], start_end[1], start_end[2], start_end[3]
            lines.append(line)
        return lines

    def build_border(self):
        """Returns a list of pyglet.shapes.Line objects"""
        return [shapes.Line(line[0], line[1], line[2], line[3], width=2, color=(0, 0, 0), batch=self.debug_batch) for
                line in self._outline_points]

    def clear_border(self):
        """Empty the stack created by build_border()"""
        self._outlines = []

    def draw_border(self):
        """Draw the border of the pymunk.Poly object"""
        for line in self._outlines:
            line.draw()

    def get_points(self):
        """Return the coordinates for the vertices of the bounding box."""
        points = self.poly.get_vertices()
        points = [self.body.local_to_world(p) for p in points]
        p_d, p_c, p_b, p_a = points
        return [(p_a, p_b), (p_b, p_c), (p_c, p_d), (p_d, p_a)]

    def collision_check(self, other):
        polyb = other
        contact = self.poly.shapes_collide(polyb)
        if contact.points:
            self._contact_points = contact.points
            return True

    def reflect(self):
        self.state_frame = self.animation.state.frame_
        self.velocity = self.body.velocity
        self.body.angle = 0
        self.body.angular_velocity = 0
        self._outline_points = self.sort_points
        self._outlines = self.build_border()
        self.x = self.body.position.x - self.size[0] // 2
        self.y = self.body.position.y - self.size[1] // 2
        self.clamp_to_screen()

        # self.shape.x = self.x
        # self.shape.y = self.y

    def clamp_to_screen(self):
        if self.x + self.size[0] < 0:
            self.body.position = (-1 + 1920, self.body.position.y)
        if self.x > 1920:
            self.body.position = (1, self.body.position.y)
        if self.y + self.size[1] < 0:
            self.body.position = (self.body.position.x, -1 + 1080)
        if self.y > 1080:
            self.body.position = (self.body.position.x, 1)

    def reduce_velocity(self):
        self.body.velocity = self.body.velocity.interpolate_to(Vec(0, 0), .5)
        self.set_action(0)

    # def move(self,direction):
    # 	self.moving = True
    # 	if direction >= 0:
    # 		self.set_action(MOVE)
    # 		dirs = DIRs[direction]
    # 		self.set_face(direction)
    # 		self.set_dir(dirs)
    # 		dirs = vDIRs[direction]
    # 		self.body.velocity = dirs*self.speed

    # def on_key(self,symbol,modifiers,intent,hold=None):
    # 	if intent == press and not self.dead:
    # 		self.take_action(symbol)
    # 	if intent == release and symbol in Movement_keys:
    # 		self.moving = False
    # 		self.reduct()
    # 		self.body.velocity = Vec(0,0)

    def take_action(self, symbol):
        pass

    def set_(self, _key, value):
        if self.__getattribute__(_key) != value:
            self.__setattr__(_key, value)
            # print(f"{str(key)} - {str(value)}")

    def set_dir(self, val):
        self.set_("direction", val)

    def set_face(self, val):
        self.set_("facing", val)

    def set_action(self, val):
        self.set_("action", val)

    def turn(self):
        self.set_face(-self.facing)

    def draw(self):
        # self.shape.draw()
        self.animation.draw()

    #       [d.draw() for d in self.debug_labels]
    #        self.draw_border()

    def update(self):
        self.age += 1
        self.reflect()
        self.animation.update()
        self.clear_border()

    def move(self, param):
        pass


class PPlayer(Player):
    def __init__(self, main_window, scene):
        self.x = 100
        self.y = 25
        self.flip = 1
        self.scene = scene
        self.jumping = False
        self.grounded = True
        self.sprint = False
        super(PPlayer, self).__init__(main_window, scene, self.x, self.y, (30, 30), (18, 49), "default")
        self.speed = 350
        self.jump_str = 225
        self.jump_amount = 0
        self.grounded = self.is_grounded(self.scene.floor)

    def is_grounded(self, floor):
        return bool(self.poly.shapes_collide(floor.poly).points)

    def stop_fall(self):
        self.y = 20

    # def get_ground(self):
    #     r = [ self.is_grounded(grnd) for grnd in [self.Scene.floor,self.Scene.floor2] ]
    #     return bool(r.count(True))

    def jump(self):
        self.set_action(2)
        if self.animation.state.frame_ in [1, 2]:
            self.body.apply_impulse_at_local_point(Vec(0, 300))
            self.body.velocity = self.body.velocity.interpolate_to(Vec(0, 300), 0.25)
        else:
            self.body.velocity = self.body.velocity.interpolate_to(Vec(0, 0), 0.8)
            self.jumping = False

        # if self.state_frame == 0:
        #     self.body.velocity = self.body.velocity.interpolate_to(Vec(0,0),1)
        # elif 0 < self.state_frame < 3:
        #     self.body.velocity = self.body.velocity.interpolate_to(Vec(self.body.velocity.x,self.jump_str),.7)
        # elif self.state_frame == 2:
        #     self.animation.state._loop = False
        # elif self.state_frame != 0 and self.grounded:
        #     self.jumping = False

    def reflect(self):
        self.grounded = self.is_grounded(self.scene.floor)
        if self.grounded:
            self.stop_fall()

        self.velocity = self.body.velocity
        self.body.angle = 0
        # self.body.angular_velocity = 0
        self._outline_points = self.sort_points
        self._outlines = self.build_border()
        self.x = self.body.position.x - 8
        self.y = self.body.position.y - 4

    def start_move(self):
        if not self.moving:
            d = [None, Vec(1, 0), Vec(-1, 0)]
            self.set_action(1)
            direction = d[self.facing]
            self.body.velocity = self.body.velocity.interpolate_to(
                Vec((direction.x * self.speed), self.body.velocity.y), .5)
            self.moving = True

    def move(self, run=None):
        d = [None, Vec(1, 0), Vec(-1, 0)]
        self.set_action(1)
        direction = d[self.facing]
        self.body.velocity = self.body.velocity.interpolate_to(Vec(direction.x * self.speed, self.body.velocity.y), 0.8)

    #            self.body.velocity = direction * self.speed

    def recv_key_press(self, symbol, modifiers):
        if symbol in [key.LEFT, key.RIGHT, key.A, key.D]:
            if symbol in L:
                self.facing = -1
            if symbol in R:
                self.facing = 1
            if modifiers & key.MOD_SHIFT:
                self.sprint = True
            self.start_move()
        elif symbol == key.SPACE:
            self.animation.state.frame_ = 0
            self.jumping = True

    def recv_key_release(self, symbol, modifiers):
        if symbol in [key.LEFT, key.RIGHT, key.A, key.D]:
            self.moving = False
        if modifiers & key.MOD_CTRL:
            pass

    def draw(self):
        super().draw()

    def update(self):
        super().update()
        if not self.moving and self.grounded and not self.jumping:
            self.reduce_velocity()
            self.stop_fall()
        if self.moving:
            self.move()
        if self.jumping:
            self.jump()


class NewPlayer(Player):
    def __init__(self, main_window, scene):
        self.x = 1920 - 64
        self.y = 1080 - 64
        self.scene = scene
        super(NewPlayer, self).__init__(main_window, scene, self.x, self.y, None, (128, 128), "default")
        self.facing = 0
        self.speed = 175
        self.destination = None
        self.destx = 0
        self.desty = 0
        self.fow = None
        self.shadow = None
        self.speed = 100
    #     self.get_fow()
    #     self.get_shadow()

    # def get_shadow(self):
    #     img = pyglet.image.load(f"{heroAssets}ashadow.png")
    #     sprite = pyglet.sprite.Sprite(img, self.x + 32, self.y + 32)
    #     self.__setattr__("shadow", sprite)

    # def get_fow(self):
    #     img = pyglet.image.load(f"{playerAssets}fog.png")
    #     sprite = pyglet.sprite.Sprite(img, self.x - 1600, self.y - 900)
    #     self.__setattr__("fow", sprite)

    def recv_key_press(self, symbol, modifiers):
        k = [key.S, key.D, key.W, key.A]
        if symbol in mv_keys:
            self.moving = True
            self.move(k.index(symbol))

    def recv_key_release(self, symbol, modifiers):
        if symbol in mv_keys:
            self.moving = False

    def move(self, direction):
        d = DIRS[direction]
        self.body.apply_impulse_at_local_point(d * self.speed)

    #        self.body.velocity = self.body.velocity.interpolate_to(d * self.speed, 1)
    # self.moving = False

    def route_(self, target):
        tgt_body = pymunk.Body()
        tgt_body.position = Vec(target[0], target[1])
        return self.body.world_to_local(tgt_body.position).normalized()

    def move_(self, dest):
        self.moving = True
        self.action = 1
        r = self.route_(dest)
        self.body.velocity = self.body.velocity.interpolate_to(Vec(r.x, r.y) * self.speed, 0.1)

    def recv_mouse_press(self, x, y, btn, modifiers):
        if btn == mouse.LEFT:
            self.set_dest((x, y))

    def set_dest(self, dest):
        self.destination = dest

    def update(self):
        super().update()
        self.fow.x = self.x - 1600 + 64
        self.fow.y = self.y - 900 + 32
        self.shadow.x = self.x + 16
        self.shadow.y = self.y
        if not self.moving:
            self.reduce_velocity()
        if self.destination is not None:
            self.move_(self.destination)
            self.destx = self.destination[0]
            self.desty = self.destination[1]
        if (self.destx >= self.x + 64 >= self.destx - 32) and (self.y + 64 >= self.y + 32 >= self.desty - 64):
            self.moving = False
            self.destination = None
            self.action = 0

    def draw(self):
        self.shadow.draw()
        super().draw()
        self.fow.draw()


class AHero(Player):
    def __init__(self, main_window, scene):
        self.x = 200
        self.y = 300
        self.scene = scene
        super(AHero, self).__init__(main_window, scene, self.x, self.y, (64, 64), (70, 85), "default")
        self.fow = None
        self.shadow = None
        self.speed = 100
    #     self.get_fow()
    #     self.get_shadow()

    # def get_shadow(self):
    #     img = pyglet.image.load(f"{heroAssets}ashadow.png")
    #     sprite = pyglet.sprite.Sprite(img, self.x + 16, self.y + 16)
    #     self.__setattr__("shadow", sprite)

    # def get_fow(self):
    #     img = pyglet.image.load(f"{playerAssets}fog.png")
    #     sprite = pyglet.sprite.Sprite(img, self.x - 1600, self.y - 900)
    #     self.__setattr__("fow", sprite)

    def recv_key_press(self, symbol, modifiers):
        if symbol in mv_keys:
            self.moving = True
            if symbol in U:
                self.facing = 2
            if symbol in R:
                self.facing = 1
            if symbol in D:
                self.facing = 0
            if symbol in L:
                self.facing = 3

    def recv_key_release(self, symbol, modifiers):
        if symbol in mv_keys:
            self.set_action(0)
            self.moving = False

    def update(self):
        super().update()
        self.fow.x = self.x - 1600 + 64
        self.fow.y = self.y - 900 + 32
        self.shadow.x = self.x + 16
        self.shadow.y = self.y
        if self.moving:
            self.set_action(1)
            self.body.velocity = self.body.velocity.interpolate_to(DIRS[self.facing] * self.speed, 0.8)
        else:
            self.body.velocity = self.body.velocity.interpolate_to(Vec(0, 0), .9)

    def draw(self):
        self.shadow.draw()
        super().draw()
        self.fow.draw()

# def cpflerpconst(f1, f2, d):
#     """Linearly interpolate from f1 to f2 by no more than d."""
#     return f1 + cpfclamp(f2 - f1, -d, d)
#
# PLAYER_VELOCITY = 100.0 * 2.0
# PLAYER_GROUND_ACCEL_TIME = 0.05
# PLAYER_GROUND_ACCEL = PLAYER_VELOCITY / PLAYER_GROUND_ACCEL_TIME
#
# PLAYER_AIR_ACCEL_TIME = 0.25
# PLAYER_AIR_ACCEL = PLAYER_VELOCITY / PLAYER_AIR_ACCEL_TIME
#
# JUMP_1080 = 16.0 * 3
# JUMP_BOOST_1080 = 24.0
# JUMP_CUTOFF_VELOCITY = 100
# FALL_VELOCITY = 250.0
#
# JUMP_LENIENCY = 0.05
#
# HEAD_FRICTION = 0.7
#
# PLATFORM_SPEED = 1
#
#
# class Player:
#     def __init__(self, main_window, scene, *args, **kwargs):
#         self.window = main_window
#         self.scene = scene
#         self.world = self.scene.world
#         self.x = 100
#         self.y = 300
#         self.1920 = 10
#         self.1080 = 48
#         self.speed = 1000
#         self.facing = 1
#         self.moving = False
#         self.grounded = False
#         self.action = 0
#         self._jumps = 2
#         self.path = f"{assetPath}player/"
#         self.age = 0
#         self.animation = AnimatedElement(self, BGLayer, "player", (self.x, self.y))
#         self.animation.init([Idle(self), Run(self)])
#         self.body = pymunk.Body(10, float("inf"), body_type=pymunk.Body.DYNAMIC)
#         self.body.position = Vec(self.x + 30, self.y - 30)
#         self.foot = pymunk.Circle(self.body, 10, (10, 22))
#         self.poly = pymunk.Poly.create_box(self.body, (self.1920, self.1080))
#         self.poly.friction = .25
#         self.ground_velocity = Vec.zero()
#         self.labels = []
#         self.world.add(self.body, self.poly)
#
#     def set_grounding(self):
#         self.__setattr__("grounding",
#                          {"normal": Vec.zero(), "penetration": Vec.zero(), "body": None, "impulse": Vec.zero(),
#                           "position": Vec.zero()})
#
#     def audit_ground(self, arbiter):
#         n = -arbiter.contact_point_set.normal
#         if n.y > self.grounding["normal"].y:
#             self.grounding["normal"] = n
#             self.grounding["penetration"] = -arbiter.contact_point_set.points[0].distance
#             self.grounding["body"] = arbiter.shapes[1].body
#             self.grounding["impulse"] = arbiter.total_impulse
#             self.grounding["position"] = arbiter.contact_point_set.points[0].point_b
#
#     def recv_key_press(self, symbol, modifiers):
#         if symbol in mv_keys:
#             if symbol in L:
#                 self.facing = -1
#             if symbol in R:
#                 self.facing = 1
#             self.body.apply_impulse_at_local_point(Vec(self.speed * self.facing, 0))
#
#     def recv_key_release(self, symbol, modifiers):
#         # if symbol in mv_keys:
#         #     self.idle_()
#         pass
#
#     def idle_(self):
#         self.action = 0
#         self.body.velocity = self.body.velocity.interpolate_to(Vec(0, 0), .8)
#         self.stop_()
#
#     def move_(self):
#         self.action = 1
#         self.body.apply_impulse_at_local_point(Vec(self.facing * 50, 0))
#         self.body.velocity = self.body.velocity.interpolate_to(Vec(self.speed * self.facing, 0), 0.8)
#
#     def stop_(self):
#         self.body.velocity = Vec(0, 0)
#
#     def is_moving(self):
#         if self.body.velocity.x != 0:
#             return True
#         else:
#             return False
#
#     def is_grounded(self):
#         if self.grounding["body"] is not None:
#             return True
#
#     def display_labels(self):
#         [ label.draw() for label in self.labels ]
#
#
#
#     def get_labels(self):
#         if self.labels != []:
#             [ label.delete() for label in self.labels ]
#             self.labels = []
#         self.labels.extend([
#             pyglet.text.Label(f"Moving: {self.moving}", font_size=10, x=10, y=1080 - 10, anchor_x="left",
#                               anchor_y="top", color=(255, 255, 255, 255)),
#             pyglet.text.Label(f"Grounded: {self.grounded}", font_size=10, x=10, y=1080 - 20, anchor_x="left",
#                                 anchor_y="top", color=(255, 255, 255, 255)),
#         ])
#
#     def reflect(self):
#         self.moving = self.is_moving()
#
#         self.body.each_arbiter(self.audit_ground)
#         self.grounded = self.is_grounded()
#         self.x = self.body.position.x - 30
#         self.y = self.body.position.y - 30
#         self.body.angle = 0
#         self.get_labels()
#
#     def update(self):
#         self.reflect()
#         if not self.moving:
#             self.idle_()
#         self.age += 1
#         self.animation.update()
#
#     def draw(self):
#         self.animation.draw()
#         self.display_labels()
