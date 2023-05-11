import logging as _logging

from ._base_entity import BaseEntity as _BaseEntity

_logging.basicConfig(level=_logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DynamicEntity(_BaseEntity):
    def __init__(self, scene, name, *args, **kwargs):
        super(DynamicEntity, self).__init__(scene, name, *args, **kwargs)
        self._destination = None
        self._last_cell = None
        self._cell_history = []
        self._path = []
        self._traveling = False
        self._movements = 10
        self._register_event_type('on_move')
        self._push_handlers(on_move=self._grid.on_move)
        self.occupy(self._cell)

    def _set_traveling(self, value):
        self._traveling = value

    def _set_destination(self, direction=None):
        if len(self._path) > 1:
            self._destination = self._grid.cells[self._path.pop(0)]
        else:
            self._destination = self._grid.cells[self._path[0]]

    def move(self):
        if self._destination is not None:
            self.vacate()
            self.occupy(self._destination)
            self._destination = None
            self._movements -= 1
            self._dispatch_event('on_move', self)

    def _get_path_to(self, _destination):
        _logging.info(f'Get path from {self._cell_name} to {self._grid[_destination].designation}')
        p = self._grid.get_path(self._cell_name, _destination)
        p.remove(self._cell_name)
        self._path = p

    def _update(self):
        if self._destination == self._cell:
            self._destination = None
            self._path = []
        if self._path:
            if not self._movements:
                self._traveling = False            
            if self._traveling:
                if self._destination is None: 
                    self._set_destination()
                else:
                    if self._destination.passable:
                        _logging.info(f'Move from {self._cell_name} to {self._destination.designation}')
                        self.move()
                    else:
                        _logging.info(f'Cell {self._destination.designation} is not passable. Character cannot proceed.')
                        self._destination = None
                        self._path = []
                        self._traveling = False
        else:
            self._traveling = False
        self.position = self._cell.coordinates
        self.x = self._position[0]
        self.y = self._position[1]