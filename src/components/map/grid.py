from __future__ import annotations

import heapq as _heapq
import random as _random
import logging as _logging
from abc import abstractmethod
from random import choice as _choice
from typing import Optional as _Optional, Union as _Union

import pyglet.event

from src.components.core.event import EventDispatcher
from src.components.misc.quiet_dict import QuietDict as _QuietDict
from .grid_blueprint import (
    print_progress,
    GridBlueprint as _GridBlueprint,
    _TERRAIN_DICT,
    save_grid as _save_grid,
    load_grid as _load_grid,
)


_logging.basicConfig(level=_logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class GridGroup:
    """
    A class to represent a group of cells on the grid.
    """

    def __init__(self, grid: Grid, title: str, cells: list, legacy: bool = False):
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

        self.cells.append(cell)
        cell.join_group(self.title, self)

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

    def __json__(self):
        """
        Serializes the GridGroup object as a JSON object.
        """
        
        cells_designations = [cell.designation for cell in self.cells]
        return {
            "title": self.title,
            "cells": cells_designations,
            "legacy": self.legacy
        }


class _AbstractGridObject:
    @abstractmethod
    def __init__(
            self,
            board: _Optional[Grid] = None,
    ):
        self.board = board


class Grid(_QuietDict):
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
        self.grid_plan = self._blueprint._grid_dictionary
        super(Grid, self).__init__()
        self._init_cell_size = cell_size
        self.cell_size = cell_size if cell_size is not None else self._blueprint._cell_size
        self.grid_scale = grid_scale if grid_scale is not None else self._blueprint._grid_scale
        _logging.info(f'Cell size {self.cell_size}')
        self.cells = {}
        _logging.info('Instantiating cells.')
        for cell in self.grid_plan.keys():
            self.cells[cell] = _Cell(cell, parentgrid=self)
            self.cells[cell]._push_handlers(on_entitle=self.on_entitle, on_divest=self.on_divest,
                                           on_occupy=self.on_occupy, on_vacate=self.on_vacate,
                                           on_obstruct=self.on_obstruct, on_destruct=self.on_destruct)
            print_progress(len(self.grid_plan.keys()), len(self.cells))
            self.update({cell: self.cells[cell]})
        self.occupied_cells = GridGroup(self, "Occupied Cells", [])
        self.obstructed_cells = GridGroup(self, "Obstructed Cells", [])
        self.entitled_cells = GridGroup(self, "Entitled Cells", [])
        self.occupants = []
        self.entities = []
        self.rows = None
        self.cols = None
        self.quadrants = None
        _logging.info('Setting up grid.')
        self._set_up()
        _save_grid(self, '001GRID.json')
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
        self._initgrid_objects()

    def _set_up_rank(self):
        _logging.info(f'Setting up {len(self._blueprint._rank)} rows')
        setattr(self, 'rows', type('rows', (list,), {}))
        exec('self.rows = self.rows()')
        for row in self._blueprint._rank:
            setattr(self.rows, f'row{row}',
                    type('Row', (list,), {'__int__': lambda self: int(self._blueprint._rank.index(row) + 1)}))
            exec(f'self.rows.row{row} = self.rows.row{row}()')
            setattr(getattr(self.rows, f'row{row}'), 'height', int(self._blueprint._rank.index(row)) * self.cell_size)            
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
            setattr(getattr(self.cols, f'col{col}'), 'width', int(self._blueprint._file.index(col)) * self.cell_size)
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

    def get_cell(self, cell_designation: _Optional[str] = None):
        return self.cells[cell_designation]
    
    def get_cell_by_index(self, index: _Optional[int] = None):
        return self.cells[self._blueprint._cell_list[index]]
    
    def get_rank_by_index(self, index: _Optional[int] = None):
        return self._blueprint._rank[index]

    def get_rank_by_height(self, height):
        for i in range(len(self.rows)):
            if self.rows[i].height <= height < self.rows[i + 1].height:
                return i

    def get_file_by_index(self, index: _Optional[int] = None):
        return self._blueprint._file[index]
    
    def get_file_by_width(self, width):
        for i in range(len(self.cols)):
            if self.cols[i].width <= width < self.cols[i + 1].width:
                return i

    def get_cell_by_position(self, x, y):
        r = self.get_rank_by_index(self.get_rank_by_height(y))
        f = self.get_file_by_index(self.get_file_by_width(x))
        return self.get_cell(f'{r}{f}')

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

    def _initgrid_objects(self):
        pass

    def _update_occupied_cells(self):
        for designation, cell in self.cells.items():
            if cell.occupied:
                if cell not in self.occupied_cells.cells:
                    self.occupied_cells.cells.append(cell)
            else:
                if cell in self.occupied_cells.cells:
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
        _save_grid(self, '001GRID.json')

    def __json__(self):
        grid_dict = {}
        grid_dict["cell_size"] = self.cell_size
        grid_dict["grid_scale"] = self.grid_scale
        grid_dict["noise_scale"] = self._blueprint._noise_scale
        grid_dict["noise_octaves"] = self._blueprint._noise_octaves
        grid_dict["noise_roughness"] = self._blueprint._noise_roughness
        
        cells_dict = {}
        for cell_designation, cell in self.cells.items():
            cell_dict = cell.__json__()
            cells_dict[cell_designation] = cell_dict
        
        grid_dict["cells"] = cells_dict
        
        return grid_dict

class _Cell(EventDispatcher):
    """
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
    __slots__ = (
        'parentgrid', 
        'entry', 
        'designation', 
        'cell_index', 
        'row', 
        'rank_index', 
        'col', 
        'file_index', 
        'coordinates', 
        'x', 
        'y', 
        'size', 
        'width', 
        'height', 
        'adjacent', 
        'terrain_str', 
        'terrain_raw', 
        'terrain_int', 
        'terrain_color', 
        'terrain_shape', 
        'quadrant_index', 
        'quadrant', 
        'occupied', 
        'occupant', 
        'passable', 
        'obstructed', 
        'obstruction', 
        'entitled', 
        'title', 
        'entity', 
        'groups', 
        'neighborhood', 
    )

    _EVENT_TYPES = ['on_occupy', 'on_vacate', 'on_obstruct', 'on_destruct', 'on_entitle', 'on_divest']
    _HANDLER_TYPES = ['occupy', 'vacate', 'obstruct', 'destruct', 'entitle', 'divest']

    def __repr__(self):
        return str(self.designation)

    def __init__(
            self,
            designation: _Optional[str] = None,
            row: _Optional[str] = None,
            col: _Optional[str] = None,
            parentgrid: _Optional[Grid] = None,
    ) -> None:
        self.parentgrid = parentgrid
        self.entry = self.parentgrid._blueprint._grid_dictionary[designation]

        self.designation = designation if designation is not None else row + col
        self.cell_index = self.entry['cell_index']

        self.row = designation[0] if row is None else row
        self.rank_index = self.entry['rank_index']

        self.col = designation[1:] if col is None else col
        self.file_index = self.entry['file_index']

        self.coordinates = self.entry['coordinates']
        self.x = self.coordinates[0]
        self.y = self.coordinates[1]

        self.size = self.parentgrid.cell_size
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
                setattr(self, key, val)

        for event in self._EVENT_TYPES:
            self._register_event_type(event)

        self.neighborhood = _Neighborhood
        
    def recv_occupant(self, occupant):
        if self.occupant is not None:
            if self.occupant == occupant:
                self._dispatch_event('on_vacate')
                return
            return
        self._dispatch_event('on_occupy', occupant)
        return
                
    def _set_quadrant(self):
        for quadrant in self.parentgrid.quadrants:
            if self.designation in quadrant['cells']:
                self.quadrant_index = self.parentgrid.quadrants.index(quadrant)
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

    def on_occupy(self, occupant):
        self.occupant = occupant
        self.occupied = True

    def on_vacate(self):
        self.occupant = None
        self.occupied = False

    def on_obstruct(self, obstruction):
        self.passable = False
        self.obstructed = True
        self.obstruction = obstruction

    def on_destruct(self):
        self.passable = True
        self.obstructed = False
        self.obstruction = None

    def get_groups(self):
        return self.groups

    def join_group(self, group_name: _Optional[str] = None, group: _Optional[GridGroup] = None):
        self.groups[group_name] = group

    def get_neighborhood(self):
        self.neighborhood(self.parentgrid, self)

    def in_neighborhood(self, neighbor):
        return self in neighbor.get_neighborhood()

    def update(self):
        for key in self.entry.keys():
            if key not in list(self.entry.keys())[:5]:
                self.entry[key] = self.__getattribute__(key)
        self.size = self.parentgrid.cell_size
        self.width = self.size
        self.height = self.size
        self.refresh()

    def refresh(self):
        self.parentgrid._blueprint._grid_dictionary[self.designation] = self.entry

    def __json__(self):
        return {
            "designation": self.designation,
            "coordinates": self.coordinates,
            "adjacent": self.adjacent,
            "occupied": self.occupied,
            "obstructed": self.obstructed,
            "entitled": self.entitled,
            "groups": [group.__json__() for group in self.groups.values()]
        }




class _Neighborhood:
    """A class to represent a neighborhood of cells.

    Args:
        grid (Grid): The grid object to which the neighborhood belongs.
        focus (_Cell): The cell object that is the focus of the neighborhood.

    Attributes:
        grid (Grid): The grid object to which the neighborhood belongs.
        focus (_Cell): The cell object that is the focus of the neighborhood.
        cell_addresses (list): A list of cell objects that are the addresses of the neighborhood.
        neighbors (list): A list of objects that are the occupants of the cells in the neighborhood
    """

    def __init__(self,
                 grid: _Optional[Grid] = None,
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
