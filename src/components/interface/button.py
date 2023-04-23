import pyglet.gui
import pyglet.sprite


from ..visual.animation import *


def _pass():
    pass


button = pyglet.gui.PushButton


class MenuButton(button):
    def __init__(self, name, x, y, img, img2, payload: dict = None):
        super(MenuButton, self).__init__(x, y, img, img2)
        self.name = name
        self.spriteA = pyglet.sprite.Sprite(img, x, y)
        self.spriteB = pyglet.sprite.Sprite(img2, x, y)
        self.hovered = False
        self.payload = payload if payload is not None else {}
        self.type = self.payload["type"]
        self.target = self.payload["target"]

        print(f"{self.name} button created with payload: {self.payload}")
        print("AABB: ", self.aabb)

    def check(self, mx, my):
        if self.aabb[0] <= mx <= self.aabb[2] and self.aabb[1] <= my <= self.aabb[3]:
            return True

        # else:
        #     if self.aabb[0] >= mx >= self.aabb[2]:
        #         if self.aabb[1] >= my >= self.aabb[3]:
        #             return False

    def on_enter(self):
        self.hovered = True

    def on_leave(self):
        self.hovered = False

    def draw(self):
        if not self.hovered:
            self.spriteA.draw()
        else:
            self.spriteB.draw()

    def on_click(self):
        print(f"Button {self.name} clicked.\n{self.payload}")
        return self.payload
