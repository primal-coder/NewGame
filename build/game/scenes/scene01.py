import random

from ..._components.core import *
from ..._components.map.board import _Grid
from ..._entities._character._base_actor import _BaseActor

_board_values = {'cell_size': 6, 'grid_scale': 1, 'noise_scale': 450, 'noise_octaves': 48, 'noise_roughness': 1.3}

_roles = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
_races = ['Dwarf', 'Elf', 'Halfling', 'Human', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling']
class Scene01(Scene):
    def __init__(self, window):
        super(Scene01, self).__init__(window, 'Scene01')
        self._window = window
        self.board = _Grid(**_board_values)
        self.player = _BaseActor(self, 'player', 'player', random.choice(_roles), random.choice(_races))

    def recv_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            destination = self.board.random_cell()
            while not destination.passable:
                destination = self.board.random_cell()
            self.player._get_path_to(destination)
        if symbol == key.ENTER:
            self.player._traveling = True
        return super().recv_key_press(symbol, modifiers)