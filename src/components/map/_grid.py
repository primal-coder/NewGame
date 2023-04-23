import random
from typing import Optional as _Optional, Tuple as _Tuple
from enum import Enum as _Enum

import numpy as _np
import noise as _noise
import json as _json
import itertools as _itertools


def print_progress(length, index):
    percentage = (index + 1) / length * 100  # Calculate the percentage value
    print(f"Progress: {percentage:.2f}%", end="\r")  # Print the percentage value on the same line


_directions = _Nw, _N, _Ne, _E, _Se, _S, _Sw, _W = ["Nw", "N", "Ne", "E", "Se", "S", "Sw", "W"]

_cell_size = 20  # The size of each cell in pixels
_grid_width = (1920*3) // _cell_size  # The width of the grid in cells, which is the width of the screen divided by the
# cell size
_grid_height = (1080*3) // _cell_size  # The height of the grid in cells, which is the height of the screen divided by
# the cell size


def _init_rows(length: _Optional[int] = None):
    """Initialize a list of rows

    """
    rows = []
    for i in range(26):
        rows.append(chr(i + 97))  # Add lowercase letters 'a' to 'z'
    for i in range(26):
        rows.append(chr(i + 65))  # Add uppercase letters 'A' to 'Z'
    for i in range(26):
        for j in range(26):
            rows.append(chr(i + 97) + chr(j + 97))  # Add two-letter strings 'aa' to 'zz'
    for i in range(1, 26):
        for j in range(26):
            rows.append(chr(i + 65) + chr(j + 97))  # Add two-letter strings 'Aa' to 'Zz'
    for i in range(26):
        for j in range(26):
            for k in range(26):
                rows.append(chr(i + 97) + chr(j + 97) + chr(k + 97))  # Add three-letter strings 'aaa' to 'zzz'
    if length:
        rows = rows[:length]  # Truncate the list to the value of the length argument, defaults to _grid_height
    print(f"{len(rows)} rows initialized.")
    return rows


_ROW_LIST = _init_rows(_grid_height)
_RANK = _ROW_LIST


class _RowEnumerator(_Enum):
    """Create an enum of the rows."""
    [exec("row{} = '{}'".format(_RANK[_], _RANK[_])) for _ in
     range(len(_RANK))]  # We use exec() to create the enum from
    # the list of rows. This is because we can't use a variable as an attribute name.


def _init_cols(length: _Optional[int] = _grid_width):
    """Initialize a list of columns, defaults to the _grid_width value."""
    cols = [str(r + 1) for r in range(length)][::-1]

    for i in range(length):
        if len(cols[i]) == 1:
            cols[i] = '0000' + cols[i]
        elif len(cols[i]) == 2:
            cols[i] = '000' + cols[i]
        elif len(cols[i]) == 3:
            cols[i] = '00' + cols[i]
        elif len(cols[i]) == 4:
            cols[i] = '0' + cols[i]


    cols.reverse()
    print(f"{len(cols)} columns initialized.")
    return cols


_COL_LIST = _init_cols()
_FILE = _COL_LIST


class _ColumnEnumerator(_Enum):
    """Create an enum of the columns."""
    [exec("col{} = '{}'".format(_FILE[_], _FILE[_])) for _ in
     range(len(_FILE))]  # We use exec() to create the enum from
    # the list of columns.


def _init_cells():
    """Initialize a list of cells."""
    cells = [r + f for r, f in _itertools.product(_RANK, _FILE)][::-1]
    cells.reverse()

    print(f"{len(cells)} cells initialized.")
    return cells


_CELLS_LIST = _init_cells()


class _CellEnumerator(_Enum):
    """Create an enum of the cells."""
    [exec("{} = '{}'".format(_CELLS_LIST[_], _CELLS_LIST[_])) for _ in range(len(_CELLS_LIST))]


def _init_adjacency(grid: _Optional[dict] = None):
    """Initialize the adjacency of each cell in the grid."""
    w = _grid_width
    for cell, information in grid.items():
        n = information['cell_index']
        print_progress(len(grid.keys()), n)
        r = grid[cell]['rank_index']
        f = grid[cell]['file_index']
        if r not in [0, len(_RANK) - 1] and f not in [0, len(_FILE) - 1]:
            """If the cell is not on the edge of the grid, then it has 8 adjacent cells."""
            grid[cell]['adjacent'] = [_CELLS_LIST[n - (w + 1)], _CELLS_LIST[n - w], _CELLS_LIST[n - (w - 1)],
                                      _CELLS_LIST[n + 1],
                                      _CELLS_LIST[n + (w + 1)], _CELLS_LIST[n + w], _CELLS_LIST[n + (w - 1)],
                                      _CELLS_LIST[n - 1]]
        else:
            if r == 0:
                if f == 0:
                    """If the cell is on the top left corner of the grid, then it has 3 adjacent cells."""
                    grid[cell]['adjacent'] = [_CELLS_LIST[1], _CELLS_LIST[w + 1], _CELLS_LIST[w]]
                elif f == len(_FILE) - 1:
                    """If the cell is on the top right corner of the grid, then it has 3 adjacent cells."""
                    grid[cell]['adjacent'] = [_CELLS_LIST[n + w], _CELLS_LIST[n + (w - 1)], _CELLS_LIST[n - 1]]
                else:
                    """If the cell is on the top edge of the grid, but not on a corner, then it has 5 adjacent cells."""
                    grid[cell]['adjacent'] = [_CELLS_LIST[n + 1], _CELLS_LIST[n + (w + 1)], _CELLS_LIST[n + w],
                                              _CELLS_LIST[n + (w - 1)],
                                              _CELLS_LIST[n - 1]]
            elif r == len(_RANK) - 1:
                if f == 0:
                    """If the cell is on the bottom left corner of the grid, then it has 3 adjacent cells."""
                    grid[cell]['adjacent'] = [_CELLS_LIST[n - w], _CELLS_LIST[n - (w - 1)], _CELLS_LIST[n + 1]]
                elif f == len(_FILE) - 1:
                    """If the cell is on the bottom right corner of the grid, then it has 3 adjacent cells."""
                    grid[cell]['adjacent'] = [_CELLS_LIST[n - (w + 1)], _CELLS_LIST[n - w], _CELLS_LIST[n - 1]]
                else:
                    """If the cell is on the bottom edge of the grid, but not on a corner, then it has 5 adjacent cells."""
                    grid[cell]['adjacent'] = [_CELLS_LIST[n - (w + 1)], _CELLS_LIST[n - w], _CELLS_LIST[n - (w - 1)],
                                              _CELLS_LIST[n + 1],
                                              _CELLS_LIST[n - 1]]
            else:
                """If the cell is on the left or right edge of the grid, but not on a corner, then it has 5 adjacent cells."""
                if f == 0:
                    grid[cell]['adjacent'] = [_CELLS_LIST[n - w], _CELLS_LIST[n - (w - 1)], _CELLS_LIST[n + 1],
                                              _CELLS_LIST[n + (w + 1)],
                                              _CELLS_LIST[n + w]]
                elif f == len(_FILE) - 1:
                    grid[cell]['adjacent'] = [_CELLS_LIST[n - (w + 1)], _CELLS_LIST[n - w], _CELLS_LIST[n + w],
                                              _CELLS_LIST[n + (w - 1)],
                                              _CELLS_LIST[n - 1]]
    print("Adjacency initialized.")


def _init_grid(_cell_size: _Optional[int] = _cell_size):
    """Create a new dictionary representing each cell on the grid. Including the coordinates, indices of the cell in respect to cells, rank and file, adjacent cells, whether
    the cell is occupied, the occupant, whether the cell is passable, whether the cell is obstructed, the obstruction, the raw float _noise value, the converted terrain integer value,
    and the groups the cell is a part of."""

    dictionary = {
        cell: {
            'coordinates': (abs(0 - ((num % len(_FILE)) * _cell_size)), abs(0 - ((num // len(_FILE)) * _cell_size))),
            # The coordinates of the cell.
            'cell_index': num,
            'rank_index': _RANK.index(cell[:-5]),
            'file_index': _FILE.index(cell[-5:]),
            'terrain_str': None,
            "terrain_raw": None,
            "terrain_int": None,
            "terrain_color": None,
            "passable": True,
            "adjacent": [],
            "occupied": False,
            "occupant": None,
            "obstructed": False,
            "obstruction": None,
            "entitled": False,
            "title": None,
            "entity": None,
            "groups": {},
        } for num, cell in enumerate(_CELLS_LIST)
    }

    _init_adjacency(dictionary)
    print("Grid initialized.")
    return dictionary


def _save_grid(dict_obj, file_path):
    """
    Exports a dictionary object to a file on disk.

    Args:
        dict_obj (dict): The dictionary object to export.
        file_path (str): The path to the file on disk to export the dictionary to.

    Returns:
        None
    """
    with open(file_path, 'w') as file:
        _json.dump(dict_obj, file)


def _load_grid(file_path: _Optional[str] = None):
    f = "empty_grid._json" or file_path
    """
    Imports a dictionary object from a file on disk.

    Args:
        file_path (str): The path to the file on disk to import the dictionary from.

    Returns:
        dict: The dictionary object imported from the file.
    """
    with open(f, 'r') as file:  # type: ignore
        dict_obj = _json.load(file)
    return dict_obj


_GRID_DICT = _init_grid()  # type: dict
_save_grid(_GRID_DICT, "empty_grid._json")

# Set the frequency and _octaves of the _noise
_scale = 55
_octaves = 36


# colors
_COBALT = (61, 89, 171)
_DODGER_BLUE = (16, 78, 139)
_DEEP_SKY_BLUE = (0, 191, 255)
_COBALT_GREEN = (107, 142, 35)
_TAN = (210, 180, 140)
_PALE_GREEN = (84, 139, 84)
_LEMON_CHIFFON = (138, 137, 112)
_LIGHT_GREY = (211, 211, 211)
_MEDIUM_GREY = (169, 169, 169)
_DIM_GREY = (121, 121, 121)
_DULL_GREY = (105, 105, 105)
_GREY = (91, 91, 91)
_DARK_GREY = (47, 47, 47)
_COLORS = [_COBALT, _DODGER_BLUE, _DEEP_SKY_BLUE, _COBALT_GREEN, _TAN, _GREY, _PALE_GREEN, _LEMON_CHIFFON, _DIM_GREY]

_TERRAIN_DICT = {
    'OCEAN': {
    'raw_max': 0.235,
    'int': 0,
    'color': _DODGER_BLUE
    },
    'LAKE': {
    'raw_max': 0.275,
    'int': 1,
    'color': _COBALT
    },
    'SHORE': {
    'raw_max': 0.295,
    'int': 2,
    'color': _DEEP_SKY_BLUE
    },
    'SAND': {
    'raw_max': 0.325,
    'int': 3,
    'color': _TAN
    },
    'SOIL': {
    'raw_max': 0.395,
    'int': 4,
    'color': _LEMON_CHIFFON
    },
    'BARREN': {
    'raw_max': 0.455,
    'int': 5,
    'color': _GREY
    },
    'GRASS': {
    'raw_max': 0.785,
    'int': 6,
    'color': _COBALT_GREEN
    },
    'HILLS': {
    'raw_max': 0.845,
    'int': 7,
    'color': _PALE_GREEN
    },
    'MOUNTAIN_BASE': {
    'raw_max': 0.865,
    'int': 8,
    'color': _DULL_GREY
    },
    'MOUNTAIN_SIDE': {
    'raw_max': 0.925,
    'int': 9,
    'color': _MEDIUM_GREY
    },
    'MOUNTAIN_PEAK': {
    'raw_max': 0.945,
    'int': 10,
    'color': _LIGHT_GREY
    },
    'MOUNTAIN_TOP': {
    'raw_max': 0.999,
    'int': 11,
    'color': (255, 255, 255)
    },
}


# Set the random seed for reproducibility
random.seed("CONTINENT")

def diamond_square(width, height, roughness):
    # Initialize the grid with zeros using NumPy
    grid = _np.zeros((height, width))

    # Set the corner values to random numbers
    grid[0, 0] = random.uniform(0.0, 1.0)
    grid[0, width-1] = random.uniform(0.0, 1.0)
    grid[height-1, 0] = random.uniform(0.0, 1.0)
    grid[height-1, width-1] = random.uniform(0.0, 1.0)

    step = width - 1
    while step > 1:
        half = step // 2

        # Diamond step
        for i in range(half, height-1, step):
            for j in range(half, width-1, step):
                average = (grid[i-half, j-half] + grid[i-half, j] +
                           grid[i, j-half] + grid[i, j]) / 4.0
                grid[i, j] = average + random.uniform(-1.0, 1.0) * roughness

        # Square step
        for i in range(0, height-1, half):
            for j in range((i+half)%step, width-1, step):
                average = (grid[(i-half+height-1) % (height-1), j] +
                           grid[(i+half) % (height-1), j] +
                           grid[i, (j+half) % (width-1)] +
                           grid[i, (j-half+width-1) % (width-1)]) / 4.0
                grid[i, j] = average + random.uniform(-1.0, 1.0) * roughness

                if i == 0:
                    grid[height-1, j] = (grid[i, j] + grid[height-2, j]) / 2.0 + random.uniform(-1.0, 1.0) * roughness

        # Reduce the roughness for each iteration
        roughness /= 2.0

        # Reduce the step size for each iteration
        step //= 2

    # Normalize the grid values to be in the range [0, 1]
    max_value = _np.max(grid)
    min_value = _np.min(grid)
    range_value = max_value - min_value
    grid = (grid - min_value) / range_value

    # Scale and shift the normalized values to be in the range [0.001, 0.999]
    grid = grid * 0.998 + 0.001

    return grid


def _generate_terrain():
    """Generate a terrain value for each cell in the inverse grid."""
    inverse_terrain_data = _np.zeros((_grid_height, _grid_width))  # type: _np.ndarray
    for y in range(_grid_width):
        for x in range(_grid_height):
            inverse_terrain_data[x][y] = _noise.pnoise2(y / _scale, x / _scale, _octaves)
    terrain_data = (inverse_terrain_data - _np.min(inverse_terrain_data)) / (_np.max(inverse_terrain_data) - _np.min(inverse_terrain_data))
    return terrain_data


def _get_terrain_value(grid: _Optional[dict] = _GRID_DICT):
    """Generate a terrain value for each cell in the grid."""
    terrain_data_ds = diamond_square(_grid_width, _grid_height, 1.676)
    terrain_data_ns = _generate_terrain()
    print(f'Diamond square terrain data generated: {terrain_data_ds.shape}\nDiamond square terrain data: {terrain_data_ds}\nNoise terrain data generated: {terrain_data_ns.shape}\nNoise terrain data: {terrain_data_ns}')
    for cell, information in grid.items():
        r, f = information['rank_index'], information['file_index']
        x, y = information['coordinates']
        terrain_ns_raw = terrain_data_ns[y // _cell_size][x // _cell_size]
        terrain_ds_raw = terrain_data_ds[r, f]
        terrain_raw = (terrain_ns_raw + terrain_ds_raw) / 2
        for terrain, info in _TERRAIN_DICT.items():
            if terrain_raw <= info['raw_max']:
                terrain_str = terrain
                terrain_int = info['int']
                terrain_color = info['color']
                break
        grid[cell]['terrain_str'] = terrain_str
        grid[cell]['terrain_raw'] = terrain_raw
        grid[cell]['terrain_int'] = terrain_int
        grid[cell]['terrain_color'] = terrain_color
    print("Terrain initialized.")


def _adjust_passability():
    """Adjust the passability of each cell in the grid."""
    for c, info in _GRID_DICT.items():
        if 3 > info['terrain_int'] > 8:
            _GRID_DICT[c]['passable'] = False


# _GRID_DICT = _load_grid("empty_grid._json") if NEW_GAME else _load_grid(f"{SAVE_FILE}")


_get_terrain_value()
_adjust_passability()


def _init_graph():
    """Create a graph of the grid."""
    graph = {}
    for cell, info in _GRID_DICT.items():
        graph[cell] = [adj for adj in info['adjacent']]
    print("Graph initialized.")
    return graph

_GRAPH = _init_graph()

_save_grid(_GRID_DICT, "001grid._json")
print("Grid saved.")
_save_grid(_GRAPH, "001graph._json")
print("Graph saved.")