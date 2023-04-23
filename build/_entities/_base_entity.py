from typing import Optional as _Optional
from .._components.event import _EventDispatcher
from .._components.map.board import _Grid


class _BaseEntity(_EventDispatcher):
    """Base class for all entities in the game. The BaseEntity is assumed to exist on a _grid, and
    has a _position, a name, and a _scale. The _scale is used to determine the size of the entity
    when it is drawn on the screen. The _scale is a tuple of two integers, the first being the
    _width, and the second being the _height. The _position is a tuple of two integers, the first
    being the _x coordinate, and the second being the _y coordinate. The name is a string that
    identifies the entity. The _grid is a reference to the _grid that the entity exists on. The
    _cell is a reference to the _cell that the entity is currently occupying. The _cell_history is
    a list of all cells that the entity has occupied. The _last_cell is a reference to the last
    _cell that the entity occupied. The BaseEntity class inherits from the EventDispatcher
    class, which allows it to dispatch events. The BaseEntity class has the following events:
        
        on_occupy: Dispatched when the entity occupies a _cell. The event handler should take
        one argument, the entity that is occupying the _cell. The event handler should be a method
        of the _cell that the entity is occupying.
        
        on_vacate: Dispatched when the entity vacates a _cell. The event handler should take
        one argument, the entity that is vacating the _cell.


    The BaseEntity class has the following methods:
    
        _get_path_to: Returns a path from the entity's current _cell to the destination _cell.
        The destination _cell can be specified as a string, which is the designation of the
        _cell, or as a Cell object.
        
        _vacate: Vacates the _cell that the entity is currently occupying. The entity will
        no longer be occupying a _cell after this method is called.
        
        _occupy: Occupies the _cell that is specified. The _cell can be specified as a string,
        which is the designation of the _cell, or as a Cell object. The entity will be
        occupying the _cell after this method is called.
        
        move: Moves the entity to the next _cell in its path. The entity will be occupying
        the next _cell in its path after this method is called.
        
        set_destination: Sets the destination of the entity to the next _cell in its path.
        The entity will be traveling to the next _cell in its path after this method is
        called.
        
        update: Updates the entity. This method should be called every frame. The entity
        will be updated after this method is called.
        
        draw: Draws the entity. This method should be called every frame. The entity will
        be drawn after this method is called.
        
        reflect: Reflects the entity's _position on the screen. This method should be called
        every frame. The entity's _position on the screen will be reflected after this method
        is called.   
    """
    def __init__(
            self,
            scene = None,
            name: _Optional[str] = None,
            _scale: _Optional[tuple[int, int]] = None,

            *arg, **kwargs
    ):
        super(_BaseEntity, self).__init__(*arg, **kwargs)
        self._scene = scene
        self._window = scene.window
        self._grid = self._scene.board
        self.name = name
        init_cell = self._grid.random_cell()
        while not init_cell.passable:
            init_cell = self._grid.random_cell()
        self._cell = init_cell 
        self._cell_name = self._cell.designation
        self._cell_history = []
        self._last_cell = None
        self._position = self._cell.coordinates
        self._scale = _scale if _scale is not None else (1, 1)
        self._x = self._position[0]
        self._y = self._position[1]
        self._width = 10 * self._scale[0]
        self._height = 10 * self._scale[1]
        self._register_event_type('on_occupy')
        self._register_event_type('on_vacate')
        self._occupy(self._cell.designation)

    def _get_path_to(self, destination: object):
        return self._grid.get_path(self._cell_name, destination)

    def _vacate(self):
        self._last_cell = self._cell
        self._cell_history.append(self._cell)
        self._cell = None
        self._cell_name = None
        self._dispatch_event('on_vacate')
        self._pop_handlers()

    def _occupy(self, cell_to_occupy: object):
        if self._cell is None:
            if not cell_to_occupy.occupied:
                self._cell = cell_to_occupy
                self._cell_name = self._cell.designation
                self._push_handlers(on_vacate=self._cell.on_vacate)
        self._dispatch_event('on_occupy', self)

    