from build.screen.stage.scene import *
from .world_objects import *

class Game1Scene(Scene):
    def __init__(self, main_window):
        super(Game1Scene, self).__init__("Game 1", main_window, world=True)
        self.treasure_chest = Container(main_window, self, "chest", (200, 400),(128,128),None)
        self.horse = Horse(main_window, self, 0, HEIGHT//2)
        self.get_level()

    def get_sheetbg(self):
        img = pyglet.image.load(f"{CWD}/build/assets/ahero/aherosheet.png")
        sprite = pyglet.sprite.Sprite(img, WIDTH - (img.width + 10), 0)
        self.__setattr__("sheetbg", sprite)

    def get_pause_screen(self):
        img = pyglet.image.load(f"{CWD}/build/assets/ui/paused.png")
        sprite = pyglet.sprite.Sprite(img, WIDTH//2 - img.width//2, HEIGHT//2, batch=self.foreground)
        self.__setattr__("pause_screen", sprite)

    def get_level(self):
        print("Loading level background ...")
        img = pyglet.image.load(f"{playerAssets}level1bg.png")
        sprite = pyglet.sprite.Sprite(img, batch=self.background)
        self.__setattr__("current_BG", sprite)


    def update(self, dt):
        super().update(dt)
        if self.active and not self.paused:
            self.player.update()
            self.treasure_chest.update()

    def draw(self):
        self.current_BG.draw()
        super().draw()
        self.treasure_chest.draw()
        self.player.draw()
        if self.paused:
            self.get_pause_screen()
            self.pause_screen.draw()

    def recv_key_press(self, symbol, modifiers):
        super().recv_key_press(symbol, modifiers)
        self.player.recv_key_press(symbol, modifiers)

    def recv_key_release(self, symbol, modifiers):
        super().recv_key_release(symbol, modifiers)
        self.player.recv_key_release(symbol, modifiers)

    def recv_mouse_press(self, x, y, btn, modifiers):
        self.click_x = x
        self.click_y = y
        super().recv_mouse_press(x, y, btn, modifiers)
        self.player.recv_mouse_press(x, y, btn, modifiers)
        if btn != mouse.LEFT:
            return
        else:
            if self.treasure_chest.check(x, y):
                self.treasure_chest.change_state(1)

    def recv_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def recv_mouse_motion(self, x, y, dx, dy):
        pass

    def recv_mouse_release(self, x, y, buttons, modifiers):
        pass

    def check_chests(self):
        if self.treasure_chest.hovered:
            if not self.treasure_chest.check(self.mouse_x, self.mouse_y):
                self.treasure_chest.on_leave()
        elif self.treasure_chest.check(self.mouse_x, self.mouse_y):
            self.treasure_chest.on_enter()
