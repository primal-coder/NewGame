from ._base_entity import _BaseEntity


class _DynamicEntity(_BaseEntity):
    def __init__(self, scene, name, *args, **kwargs):
        super(_DynamicEntity, self).__init__(scene, name, *args, **kwargs)
        self._destination = None
        self._last_cell = None
        self._cell_history = []
        self._path = []
        self._register_event_type('on_move')
        self._push_handlers(on_move=self._grid.on_move)
        self._push_handlers(on_occupy=self._cell.on_occupy, on_vacate=self._cell.on_vacate)
        self._occupy(self._cell)

    def _set_destination(self, direction=None):
        if direction is not None:
            if self._cell.designation[0] in ("a", "ad") or self._cell.designation[1:] in ("001", "100"):
                if self._cell.designation == 'a001':
                    adj_index = [3, 4, 5]
                elif self._cell.designation == 'a100':
                    adj_index = [5, 6, 7]
                elif self._cell.designation == 'ad001':
                    adj_index = [1, 2, 3]
                elif self._cell.designation == 'ad100':
                    adj_index = [0, 1, 7]
                elif self._cell.designation[:-3] == 'a':
                    adj_index = [3, 4, 5, 6, 7]
                elif self._cell.designation[:-3] == 'ad':
                    adj_index = [0, 1, 2, 3, 6]
                elif self._cell.designation[-3:] == '001':
                    adj_index = [1, 2, 3, 4, 5]
                elif self._cell.designation[-3:] == '100':
                    adj_index = [0, 1, 5, 6, 7]
            else:
                adj_index = list(range(8))
            if direction not in adj_index:
                return
            direction = adj_index.index(direction)
            self._destination = self.grid.cells[self._cell.adjacent[direction]]
        else:
            if self._path != []:
                self._destination = self.grid.cells[self._path.pop(0)]

    def move(self):
        if self._destination is not None:
            self.vacate()
            self.occupy(self._destination)
            self._destination = None
            self._dispatch_event('on_move', self)

    def _get_path_to(self, _destination):
        p = self.grid.get_path(self.cell_name, _destination)
        p.remove(self.cell_name)
        p.remove(_destination)
        self._path = p

    def _update(self):
        self.position = self._cell._coordinates
        self.x = self.position[0]
        self.y = self.position[1]

    def __str__(self):
        return f"{self.name} is at {self.position} with velocity {self.velocity}"
