from __future__ import annotations

import heapq as _heapq
import random as _random
import logging as _logging
from abc import abstractmethod
from random import choice as _choice
from typing import Optional as _Optional, Union as _Union

import pyglet.event

from src.components.core.event import EventDispatcher
from .grid_blueprint import print_progress, _GridBlueprint, _TERRAIN_DICT, _QuietDict

_logging.basicConfig(level=_logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_NEW_GAME = True  # Whether the game is new.
_SAVE_FILE = None  # The save file to load.




class _GridGroup:
    """
    A class to represent a group of cells on the grid.
    """

    def __init__(self, grid: _Grid, title: str, cells: list, legacy: bool = False):
        self.grid = grid
        self.title = title
        self.cells = [grid.cells[cell] for cell in cells]
        self.legacy = legacy
        self.initiate_group()

    def initiate_group(self):
        """Adds the group to the cells in the group."""

        for cell in self.cells:
            cell.join_group(self.title, self)

    def add_cell(self, cell):
        """Adds a cell to the group."""

        self.cells.append(self.grid.cells[cell.designation])
        self.cells[-1].join_group(self.title, self)

    def in_group(self, cell):
        """Checks if a cell is in the group"""

        cell_designations = [cell.designation for cell in self.cells]
        if cell in cell_designations:
            return True
        else:
            return False

    def remove_cell(self, cell):
        """Removes a cell from the group"""

        cell_designations = [cell.designation for cell in self.cells]
        if self.in_group(cell):
            self.cells.pop(cell_designations.index(cell))
        else:
            _logging.info("_Cell not in group!")


class _AbstractGridObject:
    @abstractmethod
    def __init__(
            self,
            board: _Optional[_Grid] = None,
    ):
        self.board = board


class _Grid(_QuietDict):
    _logging.info("Preparing mainGrid")

    def __init__(
            self,
            cell_size: _Optional[int] = None,
            grid_scale: _Optional[int] = None,
            noise_scale: _Optional[int] = None,
            noise_octaves: _Optional[int] = None,
            noise_roughness: _Optional[float] = None,
    ):
        self._blueprint = _GridBlueprint(cell_size, grid_scale, noise_scale, noise_octaves, noise_roughness)
        self.grid_plan = self._blueprint._grid
        super(_Grid, self).__init__()
        self._init_cell_size = cell_size
        self.cell_size = cell_size if cell_size is not None else self._blueprint._cell_size
        self.grid_scale = grid_scale if grid_scale is not None else self._blueprint._grid_scale
        _logging.info(f'Cell size {self.cell_size}')
        self.cells = {}
        _logging.info('Instantiating cells.')
        for cell in self.grid_plan.keys():
            self.cells[cell] = _Cell(cell, parent_grid=self)
            self.cells[cell]._push_handlers(on_entitle=self.on_entitle, on_divest=self.on_divest,
                                           on_occupy=self.on_occupy, on_vacate=self.on_vacate,
                                           on_obstruct=self.on_obstruct, on_destruct=self.on_destruct)
            print_progress(len(self.grid_plan.keys()), len(self.cells))
            self.update({cell: self.cells[cell]})
        self.occupied_cells = _GridGroup(self, "Occupied Cells", [])
        self.obstructed_cells = _GridGroup(self, "Obstructed Cells", [])
        self.entitled_cells = _GridGroup(self, "Entitled Cells", [])
        self.occupants = []
        self.entities = []
        self.rows = None
        self.cols = None
        self.quadrants = None
        _logging.info('Setting up grid.')
        self._set_up()
        self.selection = None

    def on_occupy(self, cell):
        self.occupied_cells.add_cell(cell)

    def on_vacate(self, cell):
        self.occupied_cells.remove_cell(cell)

    def on_obstruct(self, cell):
        self.obstructed_cells.add_cell(cell)

    def on_destruct(self, cell):
        self.obstructed_cells.remove_cell(cell)

    def on_entitle(self, cell):
        self.entitled_cells.add_cell(cell)

    def on_divest(self, cell):
        self.entitled_cells.remove_cell(cell)

    def on_move(self, entity):
        self._update()

    def _set_up(self):
        _logging.info('Initiating setup ...')
        self._set_up_rank()
        self._set_up_file()
        self._set_up_quadrants()
        self._set_up_cells()
        self._init_grid_objects()

    def _set_up_rank(self):
        _logging.info(f'Setting up {len(self._blueprint._rank)} rows')
        setattr(self, 'rows', type('rows', (list,), {}))
        exec('self.rows = self.rows()')
        for row in self._blueprint._rank:
            setattr(self.rows, f'row{row}',
                    type('Row', (list,), {'__int__': lambda self: int(self._blueprint._rank.index(row) + 1)}))
            exec(f'self.rows.row{row} = self.rows.row{row}()')
            exec(f'self.rows.append(self.rows.row{row})')
        _logging.info('Success.')

    def _set_up_file(self):
        _logging.info(f'Setting up {len(self._blueprint._file)} columns')
        setattr(self, 'cols', type('cols', (list,), {}))
        exec('self.cols = self.cols()')
        for col in self._blueprint._file:
            setattr(self.cols, f'col{col}',
                    type('Column', (list,), {'__int__': lambda self: int(self._blueprint._file.index(col) + 1)}))
            exec(f'self.cols.col{col} = self.cols.col{col}()')
            exec(f'self.cols.append(self.cols.col{col})')
        _logging.info('Success.')

    def _set_up_cells(self):
        _logging.info(f'Adding {len(self.cells)} cells to rows & columns.')
        for d, c in self.cells.items():
            self.rows.__getattribute__(f'row{d[:-5]}').append(c)
            self.cols.__getattribute__(f'col{d[-5:]}').append(c)
        _logging.info('Done.')
 
    def _set_up_quadrants(self):
        _logging.info(f'Setting up {len(self._blueprint._quadrants)} quadrants.')
        setattr(self, 'quadrants', type('quadrants', (list,), {}))
        exec('self.quadrants = self.quadrants()')
        quadrant_index = 0
        for quadrant, info in self._blueprint._quadrants.items():
            setattr(self.quadrants, f'quad{quadrant}',
                    type('Quadrant', (_QuietDict,), {'__int__': lambda self: int(quadrant)}))
            exec(f'self.quadrants.quad{quadrant} = self.quadrants.quad{quadrant}()')
            exec(f'self.quadrants.append(self.quadrants.quad{quadrant})')
            exec(f'self.quadrants.quad{quadrant}.update({info})')
            for cell in self.quadrants.__getattribute__(f'quad{quadrant}')['cells']:
                self.cells[cell].quadrant = quadrant
                self.cells[cell].quadrant_index = quadrant_index
            quadrant_index += 1
        _logging.info('Success.')

    def random_cell(self):
        return self.cells[_choice(self._blueprint._cell_list)]

    def random_row(self):
        return _choice([self.rows.__getattribute__(f'row{r}') for r in self._blueprint._rank])

    def random_col(self):
        return _choice([self.cols.__getattribute__(f'col{c}') for c in self._blueprint._file])

    def get_adjacent(self, cell_designation: _Optional[str] = None):
        return [self.cells[adj] for adj in self.cells[cell_designation].adjacent]

    def get_neighbors(self, cell_designation: _Optional[str] = None):
        return [self.cells[adj].occupant for adj in self.cells[cell_designation].adjacent if
                self.cells[adj].occupant is not None]

    def get_distance(self, cella: _Optional[str] = None, cellb: _Optional[str] = None,
                     measurement: _Optional[str] = None):
        m = measurement if measurement is not None else "units"
        if m == "units":
            return self._heuristic(cella, cellb)
        if m == "cells":
            return self._heuristic(cella, cellb) // 10

    def get_path(self, cella: _Optional[str] = None, cellb: _Optional[str] = None):
        return self._astar(cella, cellb)

    # Define the _heuristic function
    def _heuristic(self, cella, cellb):
        """Estimates the distance between two cells using Manhattan distance"""
        cell_a_coords = self.cells[cella].coordinates
        cell_b_coords = self.cells[cellb].coordinates
        (x1, y1) = cell_a_coords
        (x2, y2) = cell_b_coords
        return abs(x1 - x2) + abs(y1 - y2)

    # Define the _cost function
    def _cost(self, current, next):
        cell = self.cells[next]
        cost = 0
        if current not in cell.adjacent:
            """Adjusts the cost for adjacency"""
            cost += float("inf")
        else:
            if next in self.occupied_cells.cells or cell.occupied:
                cost += float("inf")
        #        if cell.obstructed:
        #            """"Adjusts the cost if the next cell is obstructed"""
        #            cost += next.obstruction.integrity // 10    # add 10% of the obstructions remaining integrity
        if not self.grid_plan[next]['passable'] or not cell.passable:
            cost += float("inf")
        """Returns the cost to move from the current cell to the next cell"""
        return cost

    # Implement A* algorithm
    def _astar(self, start, goal):
        goal_coords = self.cells[goal].coordinates
        """Finds the shortest path from start to goal in the given graph using A* algorithm"""
        frontier = [(0, start)]  # A priority queue of nodes to explore
        came_from = {}  # A dictionary that maps nodes to their parent nodes
        cost_so_far = {start: 0}  # A dictionary that maps nodes to the _cost of the best known path to that node
        graph = self._blueprint._graph

        while frontier:
            _, current = _heapq.heappop(frontier)
            current_coords = self.cells[current].coordinates
            if current_coords == goal_coords:
                # We have found the goal, reconstruct the path and return it
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for next_step in graph[current]:
                """For each neighbor of the current node, calculate the _cost of the path from the start node to that 
                neighbor"""
                new_cost = cost_so_far[current] + self._cost(current, next_step)
                if next_step not in cost_so_far or new_cost < cost_so_far[
                    next_step]:  # If the new path is better than the old path
                    cost_so_far[next_step] = new_cost  # Update the cost of the path to the neighbor
                    priority = new_cost + self._heuristic(goal, next_step)  # Calculate the priority of the neighbor
                    _heapq.heappush(frontier, (priority, next_step))  # Add the neighbor to the frontier
                    came_from[next_step] = current  # Update the neighbor's parent to the current node

        return None  # We didn't find a path

    def _init_grid_objects(self):
        pass

    def _update_occupied_cells(self):
        for designation, cell in self.cells.items():
            if cell.occupied:
                if cell not in self.occupied_cells:
                    self.occupied_cells.cells.append(cell)
            else:
                if cell in self.occupied_cells:
                    self.occupied_cells.cells.pop(self.occupied_cells.cells.index(cell))

    def _update_occupants(self):
        for designation, cell in self.cells.items():
            if cell.occupied:
                if cell.occupant not in self.occupants:
                    self.occupants.append(cell.occupant)

    def _update_lists(self):
        self._update_occupants()
        self._update_occupied_cells()

    def _update_cells(self):
        for c, cell in self.cells.items():
            cell.update()

    def _update(self):
        self._update_cells()
        self._update_lists()


class _Cell(EventDispatcher):
    """A cell on the grid.

    Args:
        designation (str): The designation of the cell on the grid. (e.g. A1, B2, etc.)

    Attributes:
        designation (str): The designation of the cell on the grid. (e.g. A1, B2, etc.)
        coordinates (tuple): The coordinates of the cell on the grid.
        adjacent (list): The adjacent cells to the cell.
        occupied (bool): Whether the cell is occupied by a piece.
        occupant (object): The object occupying the cell.
        obstructed (bool): Whether the cell is obstructed by an object.
        obstruction (object): The object obstructing the cell.
        groups (list): The groups that the cell is a member of.

    Methods:
        get_neighborhood: Returns the neighborhood of the cell.
        in_neighborhood: Returns whether the cell is in the neighborhood of another cell.
        get_distance: Returns the distance between the cell and another cell.
        get_path: Returns the path between the cell and another cell.

    """
    _EVENT_TYPES = ['on_occupy', 'on_vacate', 'on_obstruct', 'on_destruct', 'on_entitle', 'on_divest']

    def __repr__(self):
        return str(self.designation)

    def __init__(
            self,
            designation: _Optional[str] = None,
            row: _Optional[str] = None,
            col: _Optional[str] = None,
            parent_grid: _Optional[_Grid] = None,
    ) -> None:
        self.parent_grid = parent_grid
        self.entry = self.parent_grid._blueprint._grid[designation]

        self.designation = designation if designation is not None else row + col
        self.cell_index = self.entry['cell_index']

        self.row = designation[0] if row is None else row
        self.rank_index = self.entry['rank_index']

        self.col = designation[1:] if col is None else col
        self.file_index = self.entry['file_index']

        self.coordinates = self.entry['coordinates']
        self.x = self.coordinates[0]
        self.y = self.coordinates[1]

        self.size = self.parent_grid.cell_size
        self.width = self.size
        self.height = self.size

        self.adjacent = self.entry['adjacent']

        self.terrain_str = self.entry['terrain_str']
        self.terrain_raw = self.entry['terrain_raw']
        self.terrain_int = self.entry['terrain_int']
        self.terrain_color = self.entry['terrain_color']
        self.terrain_shape = self.entry['terrain_shape']

        self.quadrant_index = self.entry['quadrant_index']
        self.quadrant = self.entry['quadrant']

        self.occupied = False
        self.occupant = None
        self.passable = True
        self.obstructed = False
        self.obstruction = None

        self.entitled = False
        self.title = None
        self.entity = None

        self.groups = {}

        for key, val in self.entry.items():
            if key not in [k for k in self.entry][:7]:
                exec(f'self.{key} = {val}')

        for event in self._EVENT_TYPES:
            self._register_event_type(event)

        self.neighborhood = _Neighborhood

    def _determine_shape(self):
        """Determine the shape of the cell by assessing the adjacent cells, if an in a horizontally or vertically
        adjacent cell has the same terrain as this cell, the vertices of this cell will be used to expand the shape
        of a continuous terrain."""
        self.adjacent_terrain = []
        for cell in self.adjacent:
            self.adjacent_terrain.append(cell.terrain_str)

    def _set_quadrant(self):
        for quadrant in self.parent_grid.quadrants:
            if self.designation in quadrant['cells']:
                self.quadrant_index = self.parent_grid.quadrants.index(quadrant)
                self.entry['quadrant_index'] = self.quadrant_index
                self.entry['quadrant'] = self.quadrant

    def on_entitle(self, entity):
        self.entitled = True
        self.entity = entity
        self.title = entity.title

    def on_divest(self):
        self.entitled = False
        self.entity = None
        self.title = None
        self._dispatch_event('on_divest')

    def on_occupy(self, occupant):
        self.occupant = occupant
        self.occupied = True
        self._push_handlers(on_vacate=self.parent_grid.on_vacate)
        self._dispatch_event('on_occupy', self)

    def on_vacate(self):
        self._dispatch_event('on_vacate', self)
        self.occupant = None
        self.occupied = False

    def on_obstruct(self, obstruction):
        self.passable = False
        self.obstructed = True
        self.obstruction = obstruction
        self._dispatch_event('on_obstruct', self, obstruction)

    def on_destruct(self):
        self._dispatch_event('on_destruct', self, self.obstruction)
        self.passable = True
        self.obstructed = False
        self.obstruction = None

    def get_groups(self):
        return self.groups

    def join_group(self, group_name: _Optional[str] = None, group: _Optional[_GridGroup] = None):
        self.groups[group_name] = group

    def get_neighborhood(self):
        self.neighborhood(self.parent_grid, self)

    def in_neighborhood(self, neighbor):
        return self in neighbor.get_neighborhood()

    def update(self):
        for key in self.entry.keys():
            if key not in list(self.entry.keys())[:5]:
                self.entry[key] = self.__getattribute__(key)
        self.size = self.parent_grid.cell_size
        self.width = self.size
        self.height = self.size
        self.refresh()

    def refresh(self):
        self.parent_grid._blueprint._grid[self.designation] = self.entry


#     def draw(self):
#         self.tile.draw()

# class _TerrainTile:
#     def __init__(self, cell):
#         self.x = _GRID_DICT[cell.designation]['coordinates'][0]
#         self.y = _GRID_DICT[cell.designation]['coordinates'][1]
#         self.terrain_int = _GRID_DICT[cell.designation]['terrain_int']

#         self.terrain_type = _TERRAIN_TYPES[self.terrain_int]
#         self.color = _COLORS[self.terrain_int]
#         self.shape = _pyglet.shapes.Rectangle(self.x, self.y, 25, 25, self.color)

#     def draw(self):
#         if self.shape is not None:
#             self.shape.draw()


class _Neighborhood:
    """A class to represent a neighborhood of cells.

    Args:
        grid (_Grid): The grid object to which the neighborhood belongs.
        focus (_Cell): The cell object that is the focus of the neighborhood.

    Attributes:
        grid (_Grid): The grid object to which the neighborhood belongs.
        focus (_Cell): The cell object that is the focus of the neighborhood.
        cell_addresses (list): A list of cell objects that are the addresses of the neighborhood.
        neighbors (list): A list of objects that are the occupants of the cells in the neighborhood
    """

    def __init__(self,
                 grid: _Optional[_Grid] = None,
                 focus: _Optional[_Union[_Cell, str]] = None,
                 ):
        self.grid = grid
        self.focus = focus
        self.cell_addresses = [self.grid.cells[address] for address in self.focus.adjacent]
        self.neighbors = [address.occupant for address in self.cell_addresses if address.occupied]

    def __call__(self):
        return self.cell_addresses

    def update(self):
        self.neighbors = [address.occupant for address in self.cell_addresses if address.occupied]
