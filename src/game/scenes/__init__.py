from __future__ import annotations

from .board import Board as _Board
from .sheet import Sheet as _Sheet
from src.components.core.scene import *


class MainScene(Scene):
    def __init__(self, window):
        super(MainScene, self).__init__(window, 'MainScene')
        self.board = _Board(self.window)
        self.sheet = _Sheet(self.window, self.board.character)


window = MainWindow(dev_mode)

main_scene = MainScene(window)

#window.activate_scene('Sheet')
window.activate_scene('Board')

window.run()
