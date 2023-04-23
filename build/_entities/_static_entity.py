from typing import Optional as _Optional
from ._base_entity import _BaseEntity


class _StaticEntity(_BaseEntity):
    def __init__(self, scene, name, cell, scale: _Optional[tuple[int, int]] = None, passable: _Optional[bool] = True, *args, **kwargs):
        super(_StaticEntity, self).__init__(name, scene, cell, scale, *args, **kwargs)
        self.is_passable = passable
        self._register_event_type('on_obstruct')
        self._register_event_type('on_destruct')
        self.obstruct()

    def obstruct(self):
        if self.cell is not None:
            self._push_handlers(on_obstruct=self.cell.on_obstruct, on_destruct=self.cell.on_destruct)
        self._dispatch_event('on_obstruct', self)

    def update(self):
        self.position = self.cell._coordinates
        self.x = self.position[0]
        self.y = self.position[1]
