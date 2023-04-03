from build.screen.actors.element import *
from build.screen.actors.state import *


class AnimatedElement:
    def __init__(
            self,
            parent: Optional[object] = None,
            layer: Optional[int] = None,
            position: Optional[tuple[int, int]] = None,
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


class PPlayerAnim(AnimatedElement):
    def __init__(self, controller):
        self.layer = BGLayer
        self.x = controller.x
        self.y = controller.y
        super(PPlayerAnim, self).__init__(controller, self.layer, (self.x, self.y))

    def init(self, **kwargs):
        super().init([PIdle(self), PRun(self), PJump(self)])


class APlayerAnim(AnimatedElement):
    def __init__(self, controller):
        self.layer = BGLayer
        self.x = controller.x
        self.y = controller.y
        super(APlayerAnim, self).__init__(controller, self.layer, (self.x, self.y))

    def init(self, **kwargs):
        super().init([Actions(self)])


class AHeroAnim(AnimatedElement):
    def __init__(self, controller):
        self.layer = BGLayer
        self.x = controller.x
        self.y = controller.y
        super(AHeroAnim, self).__init__(controller, self.layer, (self.x, self.y))

    def init(self, **kwargs):
        super().init([AHeroStates(self)])


class NewPlayerAnim(AnimatedElement):
    def __init__(self, controller):
        self.layer = BGLayer
        self.x = controller.x
        self.y = controller.y
        super(NewPlayerAnim, self).__init__(controller, self.layer, (self.x, self.y))

    def init(self, **kwargs):
        super().init([NewPlayerIdle(self), NewPlayerRun(self)])


class HorseAnim(AnimatedElement):
    def __init__(self, controller):
        self.layer = BGLayer
        self.x = controller.x
        self.y = controller.y
        super(HorseAnim, self).__init__(controller, self.layer, (self.x, self.y))

    def init(self, **kwargs):
        super().init([HorseRun(self)])
