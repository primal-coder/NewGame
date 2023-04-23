#import pyglet
#import pyglet.graphics
#import pyglet.window
#import pyglet.clock

from subprocess import call as _call

def _clear():
    _call('clear')

# key = pyglet.window.key

# cell_batch = pyglet.graphics.Batch()
# # terrain types
# LAND = 0
# WATER = 1
# MOUNT = 2
# RED = (255, 0, 0, 255)
# BLUE = (0, 0, 255, 255)
# GREEN = (0, 255, 0, 255)
# YELLOW = (0, 255, 255, 255)
# PURPLE = (255, 255, 0, 255)
# COLORS = [GREEN, BLUE, RED, YELLOW, PURPLE]


# class Game(pyglet.window.Window):
#     def __init__(self):
#         super(Game, self).__init__(width=1600, height=900)
#         self.dice_set = (d4, d6, d8, d10, d12, d20)
#         self.coin = coin
#         self.main_grid = mainGrid
#         self.tile_shapes = []
#         self.player = BaseActor(self, "Player", "Player", "Fighter")
#         self.clock = pyglet.clock.Clock()
#         self.clock.schedule_interval(self.cycle, 1 / 60)
#         self.frame_count = 0
#         [d.push_handlers(on_roll=self.on_roll) for d in self.dice_set]
#         [d.push_handlers(on_rolls=self.on_rolls) for d in self.dice_set]
#         self.dice_set[-1].push_handlers(on_check=self.on_check)

#         self.labels = []

#         self.active = True
# #        self.get_grid_shape()

#     def get_grid_shape(self):
#         for cell, data in GRID_DICT.items():
#             x, y = data['coordinates']
#             terrain_raw = data['terrain_raw']
#             terrain_int = data['terrain_int']
#             shape = pyglet.shapes.Rectangle(x, y, 20, 20, COLORS[terrain_int])
#             self.tile_shapes.append(shape)

#     def on_roll(self, die_result: tuple):
#         die, result = die_result
#         print(f"{die} rolled {result}")


#     def on_rolls(self, dice_result: tuple):
#         dice, results = dice_result
#         print(f"{dice} rolled {results}")

#     def on_check(self, value):
#         print(f'{"pass" if value else "fail"}')

#     def draw_labels(self):
#         for label in self.labels:
#             label.draw()

#     def update_labels(self):
#         for label in self.labels:
#             label.update()

#     def draw_tiles(self):
#         [tile.draw() for tile in self.tile_shapes]

#     def refresh(self, dt):
#         self.flip()
#         mainGrid._update()
#         # self.player.update()
#         self.update_labels()

#     def render(self):
#         self.clear()
#         # self.draw_tiles()
#         # self.player.draw()
#         self.draw_labels()

#     def cycle(self, dt):
#         self.refresh(dt)
#         self.render()
#         self.frame_count += 1

#     def run(self):
#         while self.active:
#             self.clock.tick()
#             self.dispatch_events()
#         print("App exited.")
#         self.close()

#     def on_key_press(self, symbol, modifiers):
#         if symbol == key.ESCAPE:
#             self.active = False
#     #     if symbol == key.P:
#     #         goal_cell = mainGrid.random_cell()
#     #         while goal_cell.terrain_int != LAND:
#     #             goal_cell = mainGrid.random_cell()
#     #         else:
#     #             self.player.get_path_to(goal_cell.designation)
#     #     if symbol == key.M:
#     #         self.player.traveling = True

