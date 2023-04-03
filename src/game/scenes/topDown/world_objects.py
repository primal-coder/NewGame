from build.screen.actors.element import *


class Container(SpriteBlock):
    def __init__(self, window, scene, kind, position, dimensions, path):
        super(Container, self).__init__(window, scene, kind, position, dimensions, None, path, False, 2)
        self.aabb = (self.x, self.y, self.x + self.width, self.y + self.height)
        self.hovered = False
        self.mouse_x = 0
        self.mouse_y = 0

    def update(self):
        self.x = self.x
        self.y = self.y
        super().update()
        self.mouse_x = self.window.mouse_x
        self.mouse_y = self.window.mouse_y

    def check(self, mx, my):
        if not self.hovered and self.aabb[0] <= mx <= self.aabb[2] and self.aabb[1] <= my <= self.aabb[3]:
            return True

    def on_enter(self):
        self.hovered = True

    def on_leave(self):
        self.hovered = False

    def draw(self):
        self.sprite.draw()
        if self.hovered:
            print(f"{self.kind} hovered")
