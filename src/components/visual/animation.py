from typing import Optional as _Optional
from .element import *
from .state import *


class AnimatedElement:
    def __init__(
            self,
            parent: _Optional[object] = None,
            layer: _Optional[int] = None,
            position: _Optional[tuple[int, int]] = None,
            *args, **kwargs
    ):
        self.parent = parent
        self.facing = self.parent.facing
        self.layer = layer if layer is not None else BGLayer
        self.position = position if position is not None else (0, 0)
        self.x = self.position[0]
        self.y = self.position[1]
        self.str_path = self.__class__.__name__.replace("Anim", "").lower()
        self.path = f"{assetPath}{self.str_path}/"
        self.active_state = 0
        self.action = 0
        self.age = 0
        self.states = []
        self.state = None

    def init(self, state_list):
        self.states.extend(state_list)
        self.set_state(0)

    def set_state(self, state_index):
        self.state = self.states[state_index]

    def reflect(self):
        self.x = self.parent.x
        self.y = self.parent.y
        self.facing = self.parent.facing
        self.active_state = self.parent.action
        self.action = self.parent.action
        self.set_state(self.active_state)

    def update(self):
        self.age += 1
        self.reflect()
        self.state.update()

    def draw(self):
        self.state.draw()
