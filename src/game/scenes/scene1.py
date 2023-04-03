import pyglet.window
import pyglet.graphics
import pyglet.gl

from src.components.scene import *
from src.components.board import mainGrid

key = pyglet.window.key
mouse = pyglet.window.mouse

class Scene1(Scene):
    def __init__(self, window):
        super(Scene1, self).__init__(window, 'Scene1')
        self.label = pyglet.text.Label('Scene 1', font_name='Times New Roman', font_size=36, x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center')
        self.board = mainGrid

    def zoom(self, direction, x, y):
        cell_size = self.board.cell_size
        if direction == 'in':
            scale = 1.1
        elif direction == 'out':
            scale = 0.9

        pyglet.gl.glTranslatef(x, y, 0)
        pyglet.gl.glScalef(scale, scale, 1)
        pyglet.gl.glTranslatef(-x, -y, 0)

        cell_size /= scale

        self.board.cell_size = cell_size
    
    def zoom_in(self, x, y):
        self.zoom('in', x, y)

    def zoom_out(self, x, y):
        self.zoom('out', x, y)

    def recv_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.zoom_in(x, y)
        elif button == mouse.RIGHT:
            self.zoom_out(x, y)

    def draw_board(self):
        for designation, cell in self.board.cells.items():
            if cell.terrain_int == 0:
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (cell.x, cell.y, cell.x, cell.y + cell.height, cell.x + cell.width, cell.y + cell.height, cell.x + cell.width, cell.y)), ('c3B', (0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0)))
            elif cell.terrain_int == 1:
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (cell.x, cell.y, cell.x, cell.y + cell.height, cell.x + cell.width, cell.y + cell.height, cell.x + cell.width, cell.y)), ('c3B', (0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255)))
            elif cell.terrain_int == 2:
                pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (cell.x, cell.y, cell.x, cell.y + cell.height, cell.x + cell.width, cell.y + cell.height, cell.x + cell.width, cell.y)), ('c3B', (255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0)))
            
    def render(self):
        self.label.draw()
        self.draw_board()