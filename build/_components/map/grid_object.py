import random
from typing import Optional as _Optional
import pyglet.shapes
from src.components.map.board import _AbstractGridObject, _Grid

TITLES = {
    'null': None,
    'town': (127, 0, 127),
    'city': (189, 0, 132),
    'dungeon': (0, 255, 255)
}


class _BaseGridObject(_AbstractGridObject):
    def __init__(
            self,
            board: _Optional[_Grid] = None,
            board_position: _Optional[str] = None,
            title: _Optional[str] = None,
            color: _Optional[tuple] = None,
    ):
        self.board = board
        self.board_position = board_position
        self.title = title
        self.cell = self.board[self.board_position] if self.board is not None else None
        if self.title != 'null':
            self.cell.on_entitle(self)
        self.x = self.cell._coordinates[0] - 24 if self.cell is not None else None
        self.y = self.cell._coordinates[1] - 24 if self.cell is not None else None
        self.color = color or (255, 0, 0, 255)
        self.shape = pyglet.shapes.Rectangle(self.x, self.y, self.cell.width, self.cell.height, color=self.color)
        self.asleep = False
        self.visible = True
        self.active = True
        self.board.entities.append(self)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def sleep(self):
        self.asleep = True

    def wake(self):
        self.asleep = False

    def update(self):
        if self.active and not self.asleep:
            pass

    def draw(self):
        if self.visible:
            self.shape.draw()


class _Town(_BaseGridObject):
    def __init__(self, board, board_position):
        super(_Town, self).__init__(board, board_position, 'town', TITLES['town'])


class _City(_BaseGridObject):
    def __init__(self, board, board_position):
        super(_City, self).__init__(board, board_position, 'city', TITLES['city'])


class _Dungeon(_BaseGridObject):
    def __init__(self, board, board_position):
        super(_Dungeon, self).__init__(board, board_position, 'dungeon', TITLES['dungeon'])






