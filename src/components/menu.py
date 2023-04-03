import pyglet.image
import pyglet.sprite
import pyglet.graphics

from build.screen.stage.scene import *

uiPath = f"{assetPath}/ui/"


class Menu(Scene):
    def __init__(self, title, main_window, *args, **kwargs):
        self.is_submenu = False
        self.subs = []
        self.page = 0
        super(Menu, self).__init__(title, main_window, *args, **kwargs)
        self.on_enter()
        self.selection = self.buttons[0]

    def set_selection(self, sel):
        self.selection.on_leave()
        self.selection = self.buttons[sel]
        self.selection.on_enter()

    def sel_up(self):
        self.set_selection(self.buttons.index(self.selection) - 1 % len(self.buttons))

    def sel_down(self):
        self.set_selection(self.buttons.index(self.selection) + 1 % len(self.buttons))

    def proceed(self):
        self.button_check()

    def load_ui(self):
        print(f"Loading UI ... {CWD}/build/assets")
        img = pyglet.image.load(f"{CWD}/build/assets/ui/menuBG.png")
        sprite = pyglet.sprite.Sprite(img, batch=self.background)
        print("Loading background ...")
        self.__setattr__("bgSprite", sprite)
        print("Loading menu ...")
        self.add_button((704, 900 - 656), *create_button("Start", "Games", "sub"))
        self.add_button((725, 900 - 741), *create_button("Quit", "quit", "exit"))

    def recv_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def recv_key_press(self, symbol, modifiers):
        super().recv_key_press(symbol, modifiers)
        if symbol in [key.UP, key.W]:
            self.sel_up()
        elif symbol in [key.DOWN, key.S]:
            self.sel_down()
        elif symbol in [key.ENTER, key.SPACE]:
            self.proceed()

    def effects(self):
        if self.window.frame_count >= 100 and self.window.frame_count % 6 == 0:
            # fade_in(self.menuSprite)
            fade_in(self.buttons[0].spriteA, 10)

    def on_enter(self):
        self.load_ui()
        self.take_focus()
        self.activate()
        self.effects()

    def update(self, dt):
        if self.active and not self.paused:
            self.effects()
            self.check_buttons()
            [elem.update() for elem in self.dynamic]
            if self.page:
                img = pyglet.image.load(f"{assetPath}ui/menuBGa.png")
                sprite = pyglet.sprite.Sprite(img)
                self.bgSprite = sprite

    def draw(self):
        self.bgSprite.draw()
        self.batch.draw()
        self.foreground.draw()
        [btn.draw() for btn in self.buttons]
        [label.draw() for label in self.labels]


class Submenu(Menu):
    def __init__(self, title, main_window):
        super(Submenu, self).__init__(title, main_window)
        self.is_submenu = True
