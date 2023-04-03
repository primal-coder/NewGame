import pyglet as _pyglet
import heapq as _heapq
from random import choice as _choice
from typing import Optional as _Optional, Union as _Union

from .grid import _CellEnumerator, _ColumnEnumerator, _RowEnumerator, _cell_size, _grid_width, _grid_height, _GRID_DICT, _CELLS_LIST, _RANK, _FILE, _GRAPH, _COLORS, _TERRAIN_TYPES, _LAND, _WATER, _MOUNT

_NEW_GAME = True  # Whether the game is new.
_SAVE_FILE = None  # The save file to load.


class _GridGroup:
    """
    A class to represent a group of cells on the grid.
    """

    def __init__(self, title: str, cells: list):
        self.title = title
        self.cells = [mainGrid.cells[cell] for cell in cells]
        self.initiate_group()

    def initiate_group(self):
        """Adds the group to the cells in the group."""
    
        for cell in self.cells:
            cell.join_group(self.title, self)

    def add_cell(self, cell):
        """Adds a cell to the group."""
    
        self.cells.append(self.grid.cells[cell])
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
            print("_Cell not in group!")


class _Cell:
    """A cell on the grid.

    Args:
        designation (str): The designation of the cell on the grid. (e.g. A1, B2, etc.)

    Attributes:
        designation (str): The designation of the cell on the grid. (e.g. A1, B2, etc.)
        _coordinates (tuple): The coordinates of the cell on the grid.
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

    def __repr__(self):
        return str(self.designation)

    def __init__(
            self,
            designation: _Optional[_CellEnumerator] = None,
            row: _Optional[_RowEnumerator] = None,
            col: _Optional[_ColumnEnumerator] = None,
            parent_grid: _Optional[object] = None,
    ) -> None:
        self.parent_grid = parent_grid
        self.designation = designation if designation is not None else row + col
        self.row = designation[0] if row is None else row
        self.rank_index = _GRID_DICT[designation]['rank_index']
        self.col = designation[1:] if col is None else col
        self.file_index = _GRID_DICT[designation]['file_index']
        self._coordinates = _GRID_DICT[self.designation]['coordinates']
        self.x = self._coordinates[0]
        self.y = self._coordinates[1]
        self.size = self.parent_grid.cell_size
        self.width = self.size
        self.height = self.size
        self.adjacent = _GRID_DICT[self.designation]['adjacent']
        self.terrain_raw = _GRID_DICT[self.designation]['terrain_raw']
        self.terrain_int = _GRID_DICT[self.designation]['terrain_int']
        # self.tile = _TerrainTile(self)
        self.occupied = False
        self.occupant = None
        self.passable = True
        self.obstructed = False
        self.obstruction = None
        self.groups = {}
        for key, val in _GRID_DICT[designation].items():
            if key not in [key for key in _GRID_DICT[designation]][:6]:
                exec(f'self.{key} = {val}')
#        self.tile = _TerrainTile(self)
        self.neighborhood = _Neighborhood
#        self.shape = _pyglet.shapes.BorderedRectangle(self.x, self.y, 10, 10, 1, self.tile.color)

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

    def join_group(self, group_name: _Optional[str] = None, group: _Optional[_GridGroup] = None):
        self.groups[group_name] = group

    def get_neighborhood(self):
        self.neighborhood(mainGrid, self)

    def in_neighborhood(self, neighbor):
        return self in neighbor.get_neighborhood()

    def update(self):
        for key in _GRID_DICT[self.designation].keys():
            if key not in list(_GRID_DICT[self.designation].keys())[:5]:
                _GRID_DICT[self.designation][key] = self.__getattribute__(key)
        self.size = self.parent_grid.cell_size
        self.width = self.size
        self.height = self.siz
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

class _Grid(dict):
    def __init__(self):
        self.cell_size = 7
        self.cells = {}
        for cell in _GRID_DICT.keys():
            self.cells[cell] = _Cell(cell, parent_grid=self)
            self.update({cell:self.cells[cell]})
        self.occupied_cells = []
        self.occupants =[]
        self.groups = []
        self._set_up()
        self.selection = None

    def add_group(self, group: _Optional[_GridGroup] = None):
        if group is not None:
            self.groups.append(group)
    
    def on_move(self, entity):
        self._update()

    def _set_up(self):
        self._set_up_rank()
        self._set_up_file()
        self._set_up_cells()

    def _set_up_rank(self):
        setattr(self, 'rows', type('rows', (list,), {}))
        exec('self.rows = self.rows()')
        for row in _RANK:
            setattr(self.rows, f'row{row}',
                    type('Row', (list,), {'__int__': lambda self: int(_RANK.index(row) + 1)}))
            exec(f'self.rows.row{row} = self.rows.row{row}()')
            exec(f'self.rows.append(self.rows.row{row})')

    def _set_up_file(self):
        setattr(self, 'cols', type('cols', (list,), {}))
        exec('self.cols = self.cols()')
        for col in _FILE:
            setattr(self.cols, f'col{col}', 
                    type('Column', (list,), {'__int__': lambda self: int(_FILE.index(col) + 1)}))
            exec(f'self.cols.col{col} = self.cols.col{col}()')
            exec(f'self.cols.append(self.cols.col{col})')
        
    def _set_up_cells(self):
        for d, c in self.cells.items():
            self.rows.__getattribute__(f'row{d[:-3]}').append(c)
            self.cols.__getattribute__(f'col{d[-3:]}').append(c)

    def random_cell(self):
        return self.cells[_choice(_CELLS_LIST)]

    def random_row(self):
        return _choice([self.rows.__getattribute__(f'row{r}') for r in _RANK])

    def random_col(self):
        return _choice([self.cols.__getattribute__(f'col{c}') for c in _FILE])

    def get_adjacent(self, cell_designation: _Optional[str] = None):
        return [self.cells[adj] for adj in self.cells[cell_designation].adjacent]

    def get_neighbors(self, cell_designation: _Optional[str] = None):
        return [self.cells[adj].occupant for adj in self.cells[cell_designation].adjacent if
                self.cells[adj].occupant is not None]

    def get_distance(self, cella: _Optional[str] = None, cellb: _Optional[str] = None, measurement: _Optional[str] = None):
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
        cell_a_coords = self.cells[cella]._coordinates
        cell_b_coords = self.cells[cellb]._coordinates
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
            if next in self.occupied_cells or cell.occupied:
                cost += float("inf")
        #        if cell.obstructed:
        #            """"Adjusts the cost if the next cell is obstructed"""
        #            cost += next.obstruction.integrity // 10    # add 10% of the obstructions remaining integrity
        if not _GRID_DICT[next]['passable'] or not cell.passable:
            cost += float("inf")
        """Returns the cost to move from the current cell to the next cell"""
        return cost

    # Implement A* algorithm
    def _astar(self, start, goal):
        goal_coords = self.cells[goal]._coordinates
        """Finds the shortest path from start to goal in the given graph using A* algorithm"""
        frontier = [(0, start)]  # A priority queue of nodes to explore
        came_from = {}  # A dictionary that maps nodes to their parent nodes
        cost_so_far = {start: 0}  # A dictionary that maps nodes to the _cost of the best known path to that node
        graph = _GRAPH

        while frontier:
            _, current = _heapq.heappop(frontier)
            current_coords = self.cells[current]._coordinates
            if current_coords == goal_coords:
                # We have found the goal, reconstruct the path and return it
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for next_step in graph[current]:
                """For each neighbor of the current node, calculate the _cost of the path from the start node to that neighbor"""
                new_cost = cost_so_far[current] + self._cost(current, next_step)
                if next_step not in cost_so_far or new_cost < cost_so_far[next_step]: # If the new path is better than the old path
                    cost_so_far[next_step] = new_cost # Update the cost of the path to the neighbor
                    priority = new_cost + self._heuristic(goal, next_step) # Calculate the priority of the neighbor
                    _heapq.heappush(frontier, (priority, next_step)) # Add the neighbor to the frontier
                    came_from[next_step] = current # Update the neighbor's parent to the current node

        return None  # We didn't find a path

    def _update_occupied_cells(self):
        for designation, cell in self.cells.items():
            if cell.occupied:
                if cell not in self.occupied_cells:
                    self.occupied_cells.append(cell)
            else:
                if cell in self.occupied_cells:
                    self.occupied_cells.pop(self.occupied_cells.index(cell))

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


mainGrid = _Grid()
mainGrid.add_group(_GridGroup("Land", [c for c, cell in mainGrid.cells.items() if cell.terrain_int == _LAND]))
mainGrid.add_group(_GridGroup("Water", [c for c, cell in mainGrid.cells.items() if cell.terrain_int == _WATER]))
mainGrid.add_group(_GridGroup("Mount", [c for c, cell in mainGrid.cells.items() if cell.terrain_int == _MOUNT]))
