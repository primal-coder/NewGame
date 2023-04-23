from collections import defaultdict
import random as _random
from typing import Optional as _Optional, Tuple as _Tuple
from enum import Enum as _Enum
import logging as _logging
import numpy as _np
import noise as _noise
import json as _json
import itertools as _itertools


_logging.basicConfig(level=_logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def print_progress(length, index):
    percentage = (index + 1) / length * 100  # Calculate the percentage value
    print(f"Progress: {percentage:.2f}%", end="\r")  # Print the percentage value on the same line


_directions = _Nw, _N, _Ne, _E, _Se, _S, _Sw, _W = ["Nw", "N", "Ne", "E", "Se", "S", "Sw", "W"]

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
    'GRASS': {
    'raw_max': 0.235,
    'int': 0,
    'color': _MEDIUM_GREY
    },
    'BARREN': {
    'raw_max': 0.275,
    'int': 1,
    'color': _GREY
    },
    'SOIL': {
    'raw_max': 0.295,
    'int': 2,
    'color': _LEMON_CHIFFON
    },
    'SAND': {
    'raw_max': 0.325,
    'int': 3,
    'color': _TAN
    },
    'SHORE': {
    'raw_max': 0.335,
    'int': 4,
    'color': _DEEP_SKY_BLUE
    },
    'LAKE': {
    'raw_max': 0.455,
    'int': 5,
    'color': _COBALT
    },
    'OCEAN': {
    'raw_max': 0.785,
    'int': 6,
    'color': _DODGER_BLUE
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

class _QuietDict:
    def __init__(self):
        self.items = {}

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __delitem__(self, key):
        del self.items[key]

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, key):
        return key in self.items

    def __repr__(self):
        return repr(self.items)

    def update(self, other=None, **kwargs):
        if other:
            if hasattr(other, "keys"):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def values(self):
        return list(self.items.values())

class _GridBlueprint:
    def __init__(
            self, 
            cell_size: _Optional[int] = None, 
            grid_scale: _Optional[int] = None, 
            noise_scale: _Optional[int] = None, 
            noise_octaves: _Optional[int] = None, 
            noise_roughness: _Optional[float] = None):
        self._cell_size = cell_size if cell_size is not None else 10
        self._grid_scale = grid_scale if grid_scale is not None else 1
        self._grid_width = (1920*self._grid_scale) // self._cell_size
        self._grid_height = (1080*self._grid_scale) // self._cell_size
        self._rank = self._init_rows()
        self._file = self._init_cols()
        self._cell_list = self._init_cells()
        self._grid = self._init_grid()
        self._init_adjacency()
        self._noise_scale = noise_scale if noise_scale is not None else 100
        self._noise_octaves = noise_octaves if noise_octaves is not None else 12
        self._noise_roughness = noise_roughness if noise_roughness is not None else 0.5
        self._seed = _random.seed('CONTINENT')
        self._get_terrain_value()
        self._graph = self._init_graph()
        self.items = self._grid

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __delitem__(self, key):
        del self.items[key]

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, key):
        return key in self.items

    def __repr__(self):
        return repr(self.items)

    def _update(self, other=None, **kwargs):
        if other:
            if hasattr(other, "keys"):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def _init_rows(self):
        _logging.info(f'Initializing rows ...')
        length = self._grid_height
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
        _logging.info(f"Successfully initialized {len(rows)} rows.")
        return rows

    def _init_cols(self):
        _logging.info('Initializing columns ...')
        length = self._grid_width
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
        _logging.info(f"Successfully initialized {len(cols)} columns.")
        return cols

    def _init_cells(self):
        _logging.info('Initializing cells ...')
        cells = [r + f for r, f in _itertools.product(self._rank, self._file)][::-1]
        cells.reverse()

        _logging.info(f"Successfully initialized {len(cells)} cells.")
        return cells

    def _init_grid(self):
        _logging.info('Calculating coordinates ...')
        coordinates = [(abs(0 - ((num % len(self._file)) * self._cell_size)), abs(0 - ((num // len(self._file)) * self._cell_size))) for num in range(len(self._cell_list))]
        _logging.info('Success.')
        setattr(self, '_quadrants', self._init_quadrants(coordinates))
        dictionary = {
            cell: {
                'coordinates': coordinates[num],
                # The coordinates of the cell.
                'cell_index': num,
                'rank_index': self._rank.index(cell[:-5]),
                'file_index': self._file.index(cell[-5:]),
                'quadrant_index': None,
                'quadrant': None,
                'terrain_str': None,
                'terrain_raw': None,
                'terrain_int': None,
                'terrain_color': None,
                'terrain_shape': None,
                'passable': True,
                'adjacent': [],
                'occupied': False,
                'occupant': None,
                'obstructed': False,
                'obstruction': None,
                'entitled': False,
                'title': None,
                'entity': None,
                'groups': {},
            } for num, cell in enumerate(self._cell_list)
        }

        print("Grid initialized.")
        return dictionary\
        
    def _get_quadrant(self, coordinates):
        quadrant_x = coordinates[0] // ((self._cell_size*30) * self._grid_scale)
        quadrant_y = coordinates[1] // ((self._cell_size*30) * self._grid_scale)
        quadrant_coords = (quadrant_x, quadrant_y)
        for quadrant_index, coord in enumerate(self._quadrants):
            if coord == quadrant_coords:
                return quadrant_index

    def _init_quadrants(self, coords):
        _logging.info('Initializing quadrants ...')
        quadrants = defaultdict(dict)
        quad_cells = defaultdict(list)
        for cell_index, coord in enumerate(coords):
            # Classify cell into a quadrant based on its x and y coordinates
            quadrant_x = coord[0] // ((self._cell_size*30) * self._grid_scale)
            quadrant_y = coord[1] // ((self._cell_size*30) * self._grid_scale)
            quadrant_coords = (quadrant_x, quadrant_y)
            quad_cells[quadrant_coords].append(cell_index)
        for quadrant_index, coord in enumerate(quad_cells):
            # Create a dictionary of the cells in each quadrant
            quadrants[quadrant_index] = {
                'coordinates': coord,
                'cells': [self._cell_list[cell] for cell in quad_cells[coord]]
            }

        _logging.info(f'Successfully initialized {len(quadrants)} quadrants.')
        return quadrants


    def _init_adjacency(self):
        _logging.info('Initializing adjacency data ...')
        w = self._grid_width
        for cell, information in self._grid.items():
            n = information['cell_index']
            print_progress(len(self._grid.keys()), n)
            r = self._grid[cell]['rank_index']
            f = self._grid[cell]['file_index']
            if r not in [0, len(self._rank) - 1] and f not in [0, len(self._file) - 1]:
                self._grid[cell]['adjacent'] = [self._cell_list[n - (w + 1)], self._cell_list[n - w], self._cell_list[n - (w - 1)],
                                        self._cell_list[n + 1],
                                        self._cell_list[n + (w + 1)], self._cell_list[n + w], self._cell_list[n + (w - 1)],
                                        self._cell_list[n - 1]]
            else:
                if r == 0:
                    if f == 0:
                        self._grid[cell]['adjacent'] = [self._cell_list[1], self._cell_list[w + 1], self._cell_list[w]]
                    elif f == len(self._file) - 1:
                        self._grid[cell]['adjacent'] = [self._cell_list[n + w], self._cell_list[n + (w - 1)], self._cell_list[n - 1]]
                    else:
                        self._grid[cell]['adjacent'] = [self._cell_list[n + 1], self._cell_list[n + (w + 1)], self._cell_list[n + w],
                                                self._cell_list[n + (w - 1)],
                                                self._cell_list[n - 1]]
                elif r == len(self._rank) - 1:
                    if f == 0:
                        self._grid[cell]['adjacent'] = [self._cell_list[n - w], self._cell_list[n - (w - 1)], self._cell_list[n + 1]]
                    elif f == len(self._file) - 1:
                        self._grid[cell]['adjacent'] = [self._cell_list[n - (w + 1)], self._cell_list[n - w], self._cell_list[n - 1]]
                    else:
                        self._grid[cell]['adjacent'] = [self._cell_list[n - (w + 1)], self._cell_list[n - w], self._cell_list[n - (w - 1)],
                                                self._cell_list[n + 1],
                                                self._cell_list[n - 1]]
                else:
                    if f == 0:
                        self._grid[cell]['adjacent'] = [self._cell_list[n - w], self._cell_list[n - (w - 1)], self._cell_list[n + 1],
                                                self._cell_list[n + (w + 1)],
                                                self._cell_list[n + w]]
                    elif f == len(self._file) - 1:
                        self._grid[cell]['adjacent'] = [self._cell_list[n - (w + 1)], self._cell_list[n - w], self._cell_list[n + w],
                                                self._cell_list[n + (w - 1)],
                                                self._cell_list[n - 1]]
        _logging.info('Success.')

    def _diamond_square(self):
        _logging.info('Performing diamond square algorithmic procedure.')
        roughness = self._noise_roughness
        _logging.info(f'Roughness: {roughness}')
        # Initialize the grid with zeros using NumPy
        grid = _np.zeros((self._grid_height, self._grid_width))

        # Set the corner values to _random numbers
        grid[0, 0] = _random.uniform(0.0, 1.0)
        grid[0, self._grid_width-1] = _random.uniform(0.0, 1.0)
        grid[self._grid_height-1, 0] = _random.uniform(0.0, 1.0)
        grid[self._grid_height-1, self._grid_width-1] = _random.uniform(0.0, 1.0)

        step = self._grid_width - 1
        while step > 1:
            half = step // 2

            # Diamond step
            for i in range(half, self._grid_height-1, step):
                for j in range(half, self._grid_width-1, step):
                    average = (grid[i-half, j-half] + grid[i-half, j] +
                            grid[i, j-half] + grid[i, j]) / 4.0
                    grid[i, j] = average + _random.uniform(-1.0, 1.0) * roughness

            # Square step
            for i in range(0, self._grid_height-1, half):
                for j in range((i+half)%step, self._grid_width-1, step):
                    average = (grid[(i-half+self._grid_height-1) % (self._grid_height-1), j] +
                            grid[(i+half) % (self._grid_height-1), j] +
                            grid[i, (j+half) % (self._grid_width-1)] +
                            grid[i, (j-half+self._grid_width-1) % (self._grid_width-1)]) / 4.0
                    grid[i, j] = average + _random.uniform(-1.0, 1.0) * roughness

                    if i == 0:
                        grid[self._grid_height-1, j] = (grid[i, j] + grid[self._grid_height-2, j]) / 2.0 + _random.uniform(-1.0, 1.0) * roughness

            # Reduce the roughness for each iteration
            roughness /= 2.0

            # Reduce the step size for each iteration
            step //= 2
        
        _logging.info('Success.')
        _logging.info('Normalizing grid values.')
        # Normalize the grid values to be in the range [0, 1]
        max_value = _np.max(grid)
        min_value = _np.min(grid)
        range_value = max_value - min_value
        grid = (grid - min_value) / range_value
        _logging.info('Success.')
        _logging.info('Scaling and shifting grid values.')
        # Scale and shift the normalized values to be in the range [0.001, 0.999]
        grid = grid * 0.998 + 0.001
        _logging.info('Success.')
        _logging.info('Diamond square terrain data generated.')

        return grid


    def _generate_terrain(self):
        _logging.info('Generating noise terrain data.')
        _logging.info(f'Noise scale: {self._noise_scale}')
        _logging.info(f'Noise octaves: {self._noise_octaves}')
        inverse_terrain_data = _np.zeros((self._grid_height, self._grid_width))  # type: _np.ndarray
        for y in range(self._grid_width):
            for x in range(self._grid_height):
                inverse_terrain_data[x][y] = _noise.pnoise2(y / self._noise_scale, x / self._noise_scale, self._noise_octaves)
        _logging.info('Normalizing terrain data.')
        terrain_data = (inverse_terrain_data - _np.min(inverse_terrain_data)) / (_np.max(inverse_terrain_data) - _np.min(inverse_terrain_data))
        _logging.info('Success.')
        _logging.info('Noise terrain data generated.')
        return terrain_data


    def _get_terrain_value(self):
        terrain_data_ds = self._diamond_square()
        _logging.info(f'Shape: {terrain_data_ds.shape}')
        terrain_data_ns = self._generate_terrain()
        _logging.info(f'Shape: {terrain_data_ns.shape}')
        _logging.info('Adding ')
        for cell, information in self._grid.items():
            r, f = information['rank_index'], information['file_index']
            x, y = information['coordinates']
            terrain_ns_raw = terrain_data_ns[y // self._cell_size][x // self._cell_size]
            terrain_ds_raw = terrain_data_ds[r, f]
            terrain_raw = (terrain_ns_raw + terrain_ds_raw) / 2
            for terrain, info in _TERRAIN_DICT.items():
                if terrain_raw <= info['raw_max']:
                    terrain_str = terrain
                    terrain_int = info['int']
                    terrain_color = info['color']
                    break
            self._grid[cell]['terrain_str'] = terrain_str
            self._grid[cell]['terrain_raw'] = terrain_raw
            self._grid[cell]['terrain_int'] = terrain_int
            self._grid[cell]['terrain_color'] = terrain_color
        _logging.info('Success.')

    def _adjust_passability(self):
        _logging.info('Adjusting passability.')
        for c, info in self._grid.items():
            if 3 > info['terrain_int'] > 8:
                self._grid[c]['passable'] = False
            else:
                self._grid[c]['passable'] = True
        _logging.info('Success.')

    def _init_graph(self):
        _logging.info('Initializing graph.')
        graph = {}
        for cell, info in self._grid.items():
            graph[cell] = [adj for adj in info['adjacent']]
        _logging.info('Success.')
        return graph

def _save_grid(dict_obj, file_path):
    with open(file_path, 'w') as file:
        _json.dump(dict_obj, file)


def _load_grid(file_path: _Optional[str] = None):
    f = "empty_grid._json" or file_path
    with open(f, 'r') as file:  # type: ignore
        dict_obj = _json.load(file)
    return dict_obj
