from typing import Optional as _Optional
from enum import Enum as _Enum


import numpy as _np
import noise as _noise
import json as _json
import itertools as _itertools


_directions = _Nw, _N, _Ne, _E, _Se, _S, _Sw, _W = ["Nw", "N", "Ne", "E", "Se", "S", "Sw", "W"]
_cell_size  = 7
_grid_width = 1920 // _cell_size
_grid_height= 1080 // _cell_size

def _init_rows(length: _Optional[int] = _grid_height):
    """Initialize a list of rows, defaults to the _grid_height value."""
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
        print("Rows initialized.")
        return rows[:length]  # Truncate the list to the value of the length argument, defaults to 36
    else:
        print("Rows initialized.")
        return rows

_ROW_LIST = _init_rows()
_RANK = _ROW_LIST


class _RowEnumerator(_Enum):
    """
    Create an enum of the rows."""
    [exec("row{} = '{}'".format(_RANK[_], _RANK[_])) for _ in range(len(_RANK))]  # We use exec() to create the enum from
    # the list of rows. This is because we can't use a variable as an attribute name.

def _init_cols(length: _Optional[int] = _grid_width):
    """Initialize a list of columns, defaults to the _grid_width value."""
    cols = [str(r + 1) for r in range(length)][::-1]

    for i in range(length):
        if len(cols[i]) == 1:
            cols[i] = '00' + cols[i]
        elif len(cols[i]) == 2:
            cols[i] = '0' + cols[i]

    cols.reverse()
    print("Columns initialized.")    
    return cols

_COL_LIST = _init_cols()
_FILE = _COL_LIST


class _ColumnEnumerator(_Enum):
    """Create an enum of the columns."""
    [exec("col{} = '{}'".format(_FILE[_], _FILE[_])) for _ in range(len(_FILE))]  # We use exec() to create the enum from
    # the list of columns.

def _init_cells():
    """Initialize a list of cells."""
    cells = [r + f for r, f in _itertools.product(_RANK, _FILE)][::-1]
    cells.reverse()

    print("Cells initialized.")
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
        r = grid[cell]['rank_index']
        f = grid[cell]['file_index']        
        if r not in [0, len(_RANK) - 1] and f not in [0, len(_FILE) - 1]:
            """If the cell is not on the edge of the grid, then it has 8 adjacent cells."""
            grid[cell]['adjacent'] = [_CELLS_LIST[n - (w + 1)], _CELLS_LIST[n - w], _CELLS_LIST[n - (w - 1)], _CELLS_LIST[n + 1],
                                       _CELLS_LIST[n + (w + 1)], _CELLS_LIST[n + w], _CELLS_LIST[n + (w - 1)], _CELLS_LIST[n - 1]]
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
                    grid[cell]['adjacent'] = [_CELLS_LIST[n - w], _CELLS_LIST[n - (w - 1)], _CELLS_LIST[n + 1], _CELLS_LIST[n + (w + 1)],
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
            "coordinates": (abs(0 - ((num % len(_FILE)) * _cell_size)), abs(0 - ((num // len(_FILE)) * _cell_size))),  # The coordinates of the cell.
            "cell_index": num,
            'rank_index': _RANK.index(cell[:-3]),
            'file_index': _FILE.index(cell[-3:]),
            "terrain_raw": None,
            "terrain_int": None,
            "passable": True,
            "adjacent": [],
            "occupied": False,
            "occupant": None,
            "obstructed": False,
            "obstruction": None,
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
    with open(f, 'r') as file: # type: ignore
        dict_obj = _json.load(file)
    return dict_obj


_GRID_DICT = _init_grid() # type: dict
_save_grid(_GRID_DICT, "empty_grid._json")


# Set the frequency and _octaves of the _noise
_scale = 66
_octaves = 9

# terrain types
_LAND = 0
_WATER = 1
_MOUNT = 2
_TERRAIN_TYPES = ["_LAND","_WATER","_MOUNT"]

# colors
_RED = (255, 0, 0, 255)
_BLUE = (0, 0, 255, 255)
_GREEN = (0, 255, 0, 255)
_YELLOW = (0, 255, 255, 255)
_PURPLE = (255, 255, 0, 255)
_COLORS = [_GREEN, _BLUE, _RED, _YELLOW, _PURPLE]

# Create a numpy array to store the terrain data
def _generate_terrain():
    """Generate a terrain value for each cell in the grid."""
    terrain_data = _np.zeros((_grid_width, _grid_height)) # type: _np.ndarray
    for y in range(_grid_height):
        for x in range(_grid_width):
            terrain_data[x][y] = _noise.pnoise2(x / _scale, y / _scale, _octaves)  
    return (terrain_data - _np.min(terrain_data)) / (_np.max(terrain_data) - _np.min(terrain_data))

def _get_terrain_value(grid: _Optional[dict] = _GRID_DICT):
    """Generate a terrain value for each cell in the grid."""
    terrain_data = _generate_terrain()
    for cell, information in grid.items():
        x, y = information['coordinates']
        terrain_raw = terrain_data[x // _cell_size][y // _cell_size]
        if terrain_raw < .525:
            terrain_int = _WATER
        elif terrain_raw < .85:
            terrain_int = _LAND
        else:
            terrain_int = _MOUNT
        grid[cell]['terrain_raw'] = terrain_raw
        grid[cell]['terrain_int'] = terrain_int
    print("Terrain initialized.")

def _adjust_passability():
    """Adjust the passability of each cell in the grid."""
    for c, info in _GRID_DICT.items():
        if info['terrain_int'] != 1:
            _GRID_DICT[c]['passable'] = False


# _GRID_DICT = _load_grid("empty_grid._json") if NEW_GAME else _load_grid(f"{SAVE_FILE}")


_get_terrain_value()
_adjust_passability()


def _init_graph():
    """Create a graph of the grid."""
    graph = {}
    for cell, info in _GRID_DICT.items():
        graph[cell] = [adj for adj in info['adjacent']]
    return graph


_GRAPH = _init_graph() 

_save_grid(_GRID_DICT, "001grid._json")
_save_grid(_GRAPH, "001graph._json")