import contextlib
import pyglet
import pyglet.window
import pyglet.clock
import pyglet.graphics
from pyglet.gl import *
from subprocess import call

key = pyglet.window.key
mouse = pyglet.window.mouse


def clear():
    call("clear")


class Mode:
    """
    This class is used to represent the mode.
    It takes a string for the title and sets it as an instance attribute.
    """

    # Usage:
    # gameMode = Mode
    #("Death-match")
    def __init__(self, title: str) -> None:
        self.title = title


dev_mode = Mode("Dev")
test_mode = Mode("Test")


class MainWindow(pyglet.window.Window):
    def __init__(self, mode: Mode):
        self.mode = mode
        super(MainWindow, self).__init__(fullscreen=True)
        self.register_event_type('on_activate')
        self.register_event_type('on_deactivate')
        self.register_event_type('on_reactivate')
        self.register_event_type('on_refresh')
        self.register_event_type('on_render')
        self.fps = 1 / 60
        self.clock = pyglet.clock.Clock()
        self.frame_count = 0
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.keys_ = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dx = 0
        self.mouse_dy = 0
        self.active_scene = None
        self.scenes = {}
        self.active = True
        self.set_clock()

    def set_clock(self):
        self.clock.schedule_interval(self.cycle, self.fps)

    def deactivate_scene(self):
        self.dispatch_event('on_deactivate')

    def activate_scene(self, scene_title):
        self.dispatch_event('on_activate', scene_title)

    def reactivate_scene(self):
        self.dispatch_event('on_reactivate')

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, btn, modifiers):
        pass
            
    def on_mouse_release(self, x, y, btn, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_dx = dx
        self.mouse_dy = dy
        
    def on_key_release(self, symbol, modifiers):
        with contextlib.suppress(Exception):
            del self.keys_[symbol]

    def on_key_press(self, symbol, modifiers):
        self.keys_[symbol] = True
        if symbol == key.ESCAPE:
            self.active = False

    def refresh(self, dt):
        self.flip()
        self.dispatch_event('on_refresh', dt)

    def render(self):
        self.clear()
        self.dispatch_event('on_render')
        self.fps_display.draw()

    def cycle(self, dt):
        self.refresh(dt)
        self.render()
        self.frame_count += 1

    def run(self):
        while self.active:
            self.clock.tick()
            self.dispatch_events()
        self.close()
