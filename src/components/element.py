import pymunk
import pyglet
import pyglet.shapes
import pyglet.graphics
import pyglet.sprite

from .state import *
from .animation import *
from typing import Optional

def fade_(
        element: object,
        io: int = 1,
        degree: int = 5
):
    element.opacity += degree * io


def fade_out(element, degree=5):
    if element.opacity >= 1:
        fade_(element, -1, degree)


def fade_in(element, degree=5):
    if element.opacity <= 244:
        fade_(element, 1, degree)


class Element:
    def __init__(
            self,
            window: Optional[object],
            scene: Optional[object],
            name: Optional[str] = None,
            static: Optional[bool] = None,
            position: Optional[tuple[int, int]] = None,
            dimensions: Optional[tuple[int, int]] = None,
            shape_: Optional[int] = None,
            color: Optional[tuple[int, int, int, int]] = None,
            physical: Optional[bool] = None,
            expiration: Optional[int] = None,
            *args, **kwargs
    ):
        self.window = window
        self.scene = scene
        self.name = name if name is not None else ""
        self.static = static if static is not None else True
        if not self.static:
            self.dynamic = True
        self.position = position if position is not None else (0, 0)
        self.x = self.position[0]
        self.y = self.position[1]
        self.dimensions = dimensions if dimensions is not None else (0, 0)
        self.width = self.dimensions[0]
        self.height = self.dimensions[1]
        self.color = color if color is not None else (255, 255, 255, 255)
        self.physical = physical if physical is not None else True
        self.get_geometry(shape_)
        self.age = 0
        self.expiration = expiration if expiration is not None else 0
        self.active = True
        self.visible = True

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def get_geometry(self, shape_: Optional[int]):
        self.set_body()
        if shape_ == 0:
            self.__setattr__("shape", pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, self.color))
            self.__setattr__("poly", pymunk.Poly.create_box(self.body, (self.width, self.height)))
            self.__setattr__("rotation", self.shape.rotation)
        elif shape_ == 1:
            self.__setattr__("radius", self.dimensions[0])
            self.__setattr__("shape", pyglet.shapes.Circle(self.x, self.y, self.radius, color=self.color))
            self.__setattr__("poly", pymunk.Circle(self.body, self.width))
        self.__setattr__("opacity", self.shape.opacity)
        self.join_world()

    def join_world(self):
        self.world.add(self.body, self.poly)

    def set_body(self):
        if self.static and self.physical:
            self.__setattr__("body", pymunk.Body(10, float("inf"), pymunk.Body.STATIC))
            self.body.position = (self.x + self.width // 2, self.y + self.height // 2)
        else:
            self.__setattr__("body", pymunk.Body(10, float("inf"), pymunk.Body.DYNAMIC))
            self.body.position = (self.x + self.width // 2, self.y + self.height // 2)

    def reflect(self):
        self.x = self.body.position.x - self.width // 2
        self.y = self.body.position.y - self.height // 2
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.width = self.width
        self.shape.height = self.height

    def expire(self):
        if self.expiration != 0:
            self.active = False

    def update(self):
        if self.age > self.expiration:
            self.expire()
        if self.active and not self.static:
            self.age += 1
            self.reflect()
            self.shape.opacity = self.opacity
            #self.shape.rotation = self.rotation
        elif self.active and self.static:
            self.age += 1
        elif not self.active:
            self.scene.elements.pop(self.scene.elements.index(self)) if self.scene.elements.count(self) else None
            self.scene.dynamic_elements.pop(self.scene.dynamic_elements.index(self)) if self.scene.dynamic_elements.count(self) else None
            self.scene.static_elements.pop(self.scene.static_elements.index(self)) if self.scene.static_elements.count(self) else None
            self.world.remove(self.body, self.poly)
            self.visible = False

    def draw(self):
        if self.visible:
            self.shape.draw()


class Block(Element):
    def __init__(
            self,
            window,
            scene,
            static: Optional[bool] = None,
            position: Optional[tuple[int, int]] = None,
            dimensions: Optional[tuple[int, int]] = None,
            expiration: Optional[int] = None,
            color: Optional[tuple[int, int, int, int]] = None,
            *args, **kwargs
    ):
        super().__init__(window, scene, "Block", static, position, dimensions, 0, color, True, expiration)


class SpriteBlock(Block):
    def __init__(
            self,
            window,
            scene,
            kind: Optional[str] = None,
            position: Optional[tuple[int, int]] = None,
            dimensions: Optional[tuple[int, int]] = None,
            expiration: Optional[int] = None,
            path: Optional[str] = None,
            animated: Optional[bool] =  None,
            state_count: Optional[int] = None,
            *args,**kwargs
    ):
        self.kind = kind if kind is not None else ""
        self.patha = path if path is not None else f"{assetPath}{self.__class__.__name__.lower()}/{self.kind}a.png"
        self.animated = animated if animated is not None else False
        self.active_state = 0
        self.state_list = []
        self.sprite = None
        self.state_count = state_count if state_count is not None else 1
        for s in range(self.state_count - 1):
            self.__setattr__(f"path{'bcdefg'[s]}",f"{assetPath}{self.__class__.__name__.lower()}/{self.kind}{'bcdefg'[s]}.png")
        super(SpriteBlock,self).__init__(window,scene,position,dimensions,expiration)
        self.create_states()

    def create_states(self):
        if not self.animated and self.state_count > 1:
            for s in range(self.state_count):
                img = pyglet.image.load(self.__getattribute__(f"path{'abcdefg'[s]}"))
                self.__setattr__(f"state{'abcdefg'[s]}",pyglet.sprite.Sprite(img,self.x,self.y))
                self.state_list.append(self.__getattribute__(f"state{'abcdefg'[s]}"))
        elif self.state_count == 1:
            img = pyglet.image.load(self.patha)
            self.__setattr__("statea",pyglet.sprite.Sprite(img, self.x,self.y) )
            self.state_list.append(self.statea)

    def change_state(self, new):
        self.active_state = new

    def update(self):
        self.sprite = self.state_list[self.active_state]

    def draw(self):
        self.sprite.draw()

class Ball(Element):
    def __init__(
            self,
            window,
            scene,
            static: Optional[bool] = None,
            position: Optional[tuple[int, int]] = None,
            dimensions: Optional[tuple[int, int]] = None,
            expiration: Optional[int] = None,
            color: Optional[tuple[int, int, int, int]] = None,
            *args, **kwargs
    ):
        super().__init__(window, scene, "Ball", static, position, dimensions, 1, color, True, expiration)

