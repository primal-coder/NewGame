# %%
from abc import ABC
import contextlib
from subprocess import call
import pyglet
from pyglet.window import key, mouse


class Mode:
    """
    This class is used to represent the mode.
    It takes a string for the title and sets it as an instance attribute.
    """

    # Usage:
    # gameMode = Mode('Dev')
    def __init__(self, title: str) -> None:
        self.title = title


dev_mode = Mode('Dev')
test_mode = Mode('Test')


class MainWindow(pyglet.window.Window):
    """ 
    This class is derived from the pyglet.window.Window class and the abc.ABC metaclass. 
    It initializes the game window and register the events to be used. 
    It has various methods for handling user inputs and rendering the game. 
    The run() method runs the game loop until the user quits the game.
    """
    def __init__(self, mode: Mode) -> None:
        """
        Initializes the game window and register the events to be used.
        Sets up various attributes for handling user inputs and rendering the game.
        
        Args:
            mode (Mode): The mode of the game.
            
        Returns:
            None
            """
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

    def set_clock(self) -> None:
        """Schedules the game loop to run at the fps specified during init."""
        self.clock.schedule_interval(self.cycle, self.fps)

    def deactivate_scene(self) -> None:
        """Dispatches the 'on_deactivate' event."""
        self.dispatch_event('on_deactivate')

    def activate_scene(self, scene_title: str) -> None:
        """Dispatches the 'on_activate' event."""
        self.dispatch_event('on_activate', scene_title)

    def reactivate_scene(self) -> None:
        """Dispatches the 'on_reactivate' event."""
        self.dispatch_event('on_reactivate')

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Sets the mouse position when it is moved
        
        Args:
            x (int): The x coordinate of the mouse.
            y (int): The y coordinate of the mouse.
            dx (int): The change in x coordinate of the mouse.
            dy (int): The change in y coordinate of the mouse.

        Returns:
            None
        """
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, btn: int, modifiers: int) -> None:
        """
        Handles the mouse press event.
        
        Args:
            x (int): The x coordinate of the mouse.
            y (int): The y coordinate of the mouse.
            btn (int): The button pressed.
            modifiers (int): The modifiers pressed.
            
        Returns:
            None
        """
        pass

    def on_mouse_release(self, x: int, y: int, btn: int, modifiers: int) -> None:
        """Handles the mouse release event."""
        pass

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, btn: int, modifiers: int) -> None:
        """Handles the mouse drag event."""
        self.mouse_dx = dx
        self.mouse_dy = dy

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        with contextlib.suppress(Exception):
            del self.keys_[symbol]

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.keys_[symbol] = True
        if symbol == key.ESCAPE:
            self.active = False
        super(MainWindow, self).on_key_press(symbol, modifiers)

    def refresh(self, dt: float) -> None:
        """Flips the buffer and dispatches the 'on_refresh' event."""
        self.flip()
        self.dispatch_event('on_refresh', dt)

    def render(self) -> None:
        """Clears the screen and dispatches the 'on_render' event."""
        self.clear()
        self.dispatch_event('on_render')
        self.fps_display.draw()

    def cycle(self, dt: float) -> None:
        """Calls the refresh and render methods and increments the frame count."""
        self.refresh(dt)
        self.render()
        self.frame_count += 1

    def run(self) -> None:
        """Runs the game loop until the user quits the game."""
        while self.active:
            self.clock.tick()
            self.dispatch_events()
        self.close()

# %%
