from src.components.core.window import *

import pyglet.event
import pyglet.graphics

import pymunk


#  Handlers

HANDLERS = {
    'on_key_press': 'recv_key_press',
    'on_key_release': 'recv_key_release',
    'on_mouse_press': 'recv_mouse_press',
    'on_mouse_release': 'recv_mouse_release',
    'on_mouse_drag': 'recv_mouse_drag',
    'on_mouse_motion': 'recv_mouse_motion',
    'on_refresh': 'refresh',
    'on_render': 'render',
}


class Scene(pyglet.event.EventDispatcher):
    """A scene is a collection of elements that can be rendered and updated.
    """
    def __init__(
            self,
            window: MainWindow,
            title: str = None,
            physics: bool = False,
            *args, **kwargs
    ):
        super(Scene, self).__init__()
        self.title = title
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.elements = []
        self.static_elements = []
        self.dynamic_elements = []
        self.world = pymunk.Space()
        self.world.gravity = (0, -1000)
        self.active = False
        self.link()

    def link(self):
        self.window.scenes[self.title] = self
        self.window.push_handlers(on_activate=lambda scene_title: self.activate(scene_title))

    def activate(self, scene_title):
        if scene_title == self.title:
            if self.window.active_scene is not None:
                if self.window.active_scene != self:
                    self.window.deactivate_scene()
                else:
                    return

            self.active = True
            self.window.active_scene = self
            self.window.set_handler('on_deactivate', self.deactivate)
            self.window.set_handler('on_reactivate', self.reactivate)
            for event_type in self.window.event_types:
                if event_type in HANDLERS:
                    self.window.set_handler(event_type, getattr(self, HANDLERS[event_type]))

    def deactivate(self):
        self.active = False
        self.window.active_scene = None
        self.window.remove_handler('on_deactivate', self.deactivate)
        for event_type in self.window.event_types:
            if event_type in HANDLERS:
                self.window.remove_handler(event_type, getattr(self, HANDLERS[event_type]))

    def reactivate(self):
        self.deactivate()
        self.__init__(self.window, self.title)
        self.activate(self.title)

    def create_element(self):
        pass

    def add_element(self, element):
        self.elements.append(element)

    def add_static_element(self, element):
        self.static_elements.append(element)
        self.batch.add(element.vertex_list)

    def add_dynamic_element(self, element):
        self.dynamic_elements.append(element)
        self.batch.add(element.vertex_list)

    def recv_key_press(self, symbol, modifiers):
        pass

    def recv_key_release(self, symbol, modifiers):
        pass

    def recv_mouse_press(self, x, y, btn, modifiers):
        pass

    def recv_mouse_release(self, x, y, btn, modifiers):
        pass

    def recv_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def recv_mouse_motion(self, x, y, dx, dy):
        pass

    def refresh(self, dt):
        pass

    def render(self):
        if self.active:
            self.batch.draw()
