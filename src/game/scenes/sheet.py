from src.components.interface.notation import DynamicLabel as _DynamicLabel, Label as _Label, Message as _Message
from src.components.entity.actor.base_actor import _BaseActor, _key
from src.components.core.scene import Scene as _Scene

class Sheet(_Scene):
    def __init__(self, window, actor: _BaseActor):
        super(Sheet, self).__init__(window, 'Sheet')
        self.actor = actor
        self.labels = []
        self.dynamic_labels = []
        self._set_up()

    def recv_key_press(self, symbol, modifiers):
        if symbol == _key.C:
            self.window.deactivate_scene()
            self.window.activate_scene('Board')
    def _set_up(self):
        for key, value in self.actor.__dict__.items():
            if not key.startswith('_'):
                self.dynamic_labels.append(_DynamicLabel(self.actor, key, 100, 950 - len(self.dynamic_labels) * 15, index=2))

    def refresh(self, dt):
        self.actor._update()
        for label in self.dynamic_labels:
            label.update()

    def render(self):
        for label in self.labels:
            label.draw()
        for label in self.dynamic_labels:
            label.draw()