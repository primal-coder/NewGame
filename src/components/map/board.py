import logging as _logging
import math
import random
from collections import defaultdict
import pyglet.window
import pyglet.graphics
import pyglet.gl
from pyglet.gl import *

from src.components.core.scene import *
from src.components.core.turn import *
from src.components.map.grid import Grid as _Grid, _TERRAIN_DICT
from src.components.entity.actor.base_actor import _BaseActor

# from src.components.player.actor._base_actor import _BaseActor

_logging.basicConfig(level=_logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

key = pyglet.window.key
mouse = pyglet.window.mouse

_board_values = {'cell_size': 12, 'grid_scale': 1, 'noise_scale': 370, 'noise_octaves': 36, 'noise_roughness': 1.29}


def _create_displacement_map(noise_texture, width, height):
    grayscale_data = noise_texture.get_image_data().get_data('L')
    scale_factor = 32.0
    displacement_data = bytearray(width * height * 2)
    for y in range(height):
        for x in range(width):
            grayscale_value = grayscale_data[y * width + x]
            displacement = int(scale_factor * (grayscale_value / 255.0 - 0.5))
            displacement_data[(y * width + x) * 2:(y * width + x) * 2 + 2] = displacement.to_bytes(2, 'little',
                                                                                                   signed=True)
    displacement_map = pyglet.image.ImageData(width, height, 'RGB', displacement_data)
    return displacement_map


def _create_distortion_shader(displacement_map):
    vertex_shader = '''
        #version 120

        varying vec2 v_texcoord;
        uniform mat4 gl_ModelViewProjectionMatrix;
        uniform vec2 displacement_factor;

        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            v_texcoord = gl_MultiTexCoord0.xy + displacement_factor * texture2D(gl_TextureMatrix[0], gl_MultiTexCoord0.xy).rg;
        }
    '''
    fragment_shader = '''
        #version 120

        varying vec2 v_texcoord;
        uniform sampler2D texture;

        void main() {
            vec2 texcoord = v_texcoord;
            texcoord.x = 1.0 - texcoord.x;
            gl_FragColor = texture2D(texture, texcoord);
        }
    '''

    program = pyglet.graphics.shader.ShaderProgram(
        vertex_shader,
        fragment_shader
    )
    program.bind()

    # Set the displacement map texture
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(displacement_map.target, displacement_map.id)
    glUniform1i(program.uniforms['displacement_map'], 1)

    # Set the displacement and scale factors
    program.uniforms['displacement_factor'] = (0.01, 0.02)
    program.uniforms['scale_factor'] = (0.005,)

    return program


class Board(Scene):
    def __init__(self, window):
        super(Board, self).__init__(window, 'Board')

        # self.label = pyglet.text.Label('Scene 1', font_name='Times New Roman', font_size=36, x=window.width // 2,
        #                                y=window.height // 2, anchor_x='center', anchor_y='center')
        self.board = _Grid(**_board_values)
        self.character = _BaseActor(self, 'Player', 'Player', 'Fighter', 'Human')
        self.enemy = _BaseActor(self, 'Enemy', 'Enemy', 'Fighter', 'Human')
        self.cell_size = _board_values['cell_size']
        self.zoom_scale = 1
        self.board_width = _board_values['grid_scale'] * self.window.width
        self.board_height = _board_values['grid_scale'] * self.window.height
        self.board_left = self.window.width // 2 - self.board_width // 2
        self.board_top = self.window.height // 2 + self.board_height // 2
        self.board_right = self.board_left + self.board_width
        self.board_bottom = self.board_top - self.board_height
        self.center_x = self.window.width // 2
        self.center_y = self.window.height // 2
        self.prev_x = self.center_x
        self.prev_y = self.center_y
        self.pan_dx = 0
        self.pan_dy = 0
        self.dirty_flag = True
        self.vertices = []
        self.selected_cell = None
        self.transitioning = False
        self.turn_manager = TurnManager(self.window, self.character, self.enemy)

    def take_screenshot(self):
        pyglet.image.get_buffer_manager().get_color_buffer().save('screen.png')

    def load_screen_image(self):
        return pyglet.image.load('screen.png')

    def _create_noise_texture(self, width, height):
        data = bytearray(width * height * 3)

        gradient_vectors = []
        for i in range(256):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            gradient_vectors.append((x, y))

        scale = 16
        for y in range(height):
            for x in range(width):
                cell_x = int(x / scale)
                cell_y = int(y / scale)

                corner_indices = [
                    (cell_y * 256 + (cell_x + 1)) % 256,
                    ((cell_y + 1) * 256 + (cell_x + 1)) % 256,
                    ((cell_y + 1) * 256 + cell_x) % 256,
                    (cell_y * 256 + cell_x) % 256
                ]

                corner_dist_vectors = [
                    (x - (cell_x + 1)) * scale + gradient_vectors[corner_indices[0]][0],
                    (y - cell_y) * scale + gradient_vectors[corner_indices[1]][1],
                    (x - cell_x) * scale + gradient_vectors[corner_indices[2]][0],
                    (y - (cell_y + 1)) * scale + gradient_vectors[corner_indices[3]][1]

                ]

                dot_products = []
                for i in range(4):
                    dot_products.append(corner_dist_vectors[i] * gradient_vectors[corner_indices[i]][0] +
                                        corner_dist_vectors[i] * gradient_vectors[corner_indices[i]][1])

                u = x / scale - cell_x
                v = y / scale - cell_y
                noise = (1 - u) * (1 - v) * dot_products[0] + u * (1 - v) * dot_products[1] + u * v * dot_products[
                    2] + (1 - u) * v * dot_products[3]
                noise = (noise / 2.0 + 0.5) * 255
                noise = max(min(noise, 255), 0)

                base_index = (y * width + x) * 3
                data[base_index] = int(noise)
                data[base_index + 1] = int(noise)
                data[base_index + 2] = int(noise)

        image_data = pyglet.image.ImageData(width, height, 'RGB', bytes(data))
        noise_texture = image_data.create_texture(pyglet.image.Texture)
        return noise_texture, width, height

    def _transition_animation(self):
        self.take_screenshot()
        setattr(self, 'screenshot_image', self.load_screen_image())

        noise_texture, width, height = self._create_noise_texture(self.screenshot_image.width,
                                                                  self.screenshot_image.height)
        displacement_map = _create_displacement_map(noise_texture, width, height)

        setattr(self, 'screen_sprite', pyglet.sprite.Sprite(self.screenshot_image))
        self.screen_sprite.shader = _create_distortion_shader(displacement_map)

    def is_within_board(self, x, y):
        return self.board_left < x < self.board_right and self.board_bottom < y < self.board_top

    def update_center(self, x=None, y=None):
        x = x if x is not None else self.center_x
        y = y if y is not None else self.center_y
        self.prev_x, self.prev_y = self.center_x, self.center_y
        x += self.pan_dx
        y += self.pan_dy
        self.center_x, self.center_y = x, y

    def update_board_edges(self):
        half_width = (self.window.width // 2) * _board_values['grid_scale']
        half_height = (self.window.height // 2) * _board_values['grid_scale']
        self.board_left -= self.center_x + half_width
        self.board_right += self.center_x + half_width
        self.board_top += self.center_y + half_height
        self.board_bottom -= self.center_y + half_height

    def next_turn(self):
        _logging.info('Next Turn...')
        self.turn_manager.next_turn()
        self.turn_manager.get_current_actor()._movements = 10
        _logging.info(f'Current Actor: {self.turn_manager.get_current_actor().name}')

    def enemy_move(self):
        _logging.info('Enemy Move...')
        self.turn_manager.get_current_actor()._get_path_to(self.character._cell_name)
        self.turn_manager.get_current_actor()._set_traveling(True)

    def enemy_turn(self):
        if not self.enemy._path:
            self.enemy_move()
        if not self.enemy._movements:
            self.enemy._path = []
            self.next_turn()
        if self.enemy._cell_name == self.character._cell_name:
            self.transitioning = True

    def recv_mouse_press(self, x, y, btn, modifiers):
        if btn == mouse.LEFT:
            _logging.info(f'Left click @ {x}, {y}')
            x_ = int((x - self.board_left) / self.zoom_scale) - self.pan_dx
            y_ = int((y - self.board_bottom) / self.zoom_scale) - self.pan_dy
            if (x, y) != (x_, y_):
                _logging.info(f'Translated left click to {x_}, {y_}')
                if self.is_within_board(x_, y_):
                    self.selected_cell = self.board.get_cell_by_position(x_, y_)
                    if self.selected_cell is not None:
                        _logging.info(f'Selected cell: {self.selected_cell.designation}')
                        self.character._get_path_to(self.selected_cell.designation)
                        self.character._set_traveling(True)
                    else:
                        _logging.info(f'Left click @ {x}, {y} - None')
        return super().recv_mouse_press(x, y, btn, modifiers)

    def recv_key_release(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.pan_dx = 0
        elif symbol == key.RIGHT:
            self.pan_dx = 0
        elif symbol == key.UP:
            self.pan_dy = 0
        elif symbol == key.DOWN:
            self.pan_dy = 0
        return super().recv_key_release(symbol, modifiers)

    def recv_key_press(self, symbol, modifiers):
        pan_strength = 100
        zoom_step = 0.25
        if symbol == key.EQUAL:
            self.zoom_scale -= zoom_step
        elif symbol == key.MINUS:
            self.zoom_scale += zoom_step
        if symbol == key.LEFT:
            self.pan_dx = -pan_strength
        elif symbol == key.RIGHT:
            self.pan_dx = pan_strength
        elif symbol == key.UP:
            self.pan_dy = pan_strength
        elif symbol == key.DOWN:
            self.pan_dy = -pan_strength
        if symbol == key.C:
            self.deactivate()
            self.window.activate_scene('Sheet')
        if symbol == key.SPACE:
            if self.turn_manager.get_current_actor() == self.character:
                self.next_turn()
        return super().recv_key_press(symbol, modifiers)

    def calculate_vertices(self, x, y):
        x += self.center_x - self.prev_x
        y += self.center_y - self.prev_y
        width, height = self.cell_size - ((self.zoom_scale - 1) // 1), self.cell_size - ((self.zoom_scale - 1) // 1)
        return [x, y, x, y + height - 1, x + width - 1, y + height - 1,
                x + width - 1, y]

    def prepare_vertices(self):
        terrains = defaultdict(list)
        # Draw each quadrant as a single shape
        for quadrant in self.board.quadrants:
            for cell in list(quadrant.values())[1]:
                cell = self.board.cells[cell]
                verts = self.calculate_vertices(cell.x, cell.y)
                # Perform vertex simplification
                threshold = 0.1  # Adjust as needed
                simplified_verts = []
                for i in range(0, len(verts), 2):
                    if i + 1 >= len(verts):
                        break
                    cur_vert = verts[i:i + 2]
                    if not simplified_verts:
                        simplified_verts.extend(cur_vert)
                    else:
                        prev_vert = simplified_verts[-2:]
                        dist = math.sqrt((cur_vert[0] - prev_vert[0]) ** 2 + (cur_vert[1] - prev_vert[1]) ** 2)
                        if dist > threshold:
                            simplified_verts.extend(cur_vert)
                verts = simplified_verts
                terrain_key = cell.terrain_str
                terrains[terrain_key] += verts
        return terrains

    def draw_objects(self):
        if getattr(self, 'dirty_flag', True):
            self.vertices = self.prepare_vertices()
            self.dirty_flag = False

        # Draw each terrain type as a single shape
        terrains = self.vertices
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glPushMatrix()
        pyglet.gl.glLoadIdentity()
        min_x = self.center_x - (self.window.width / 2) * self.zoom_scale
        max_x = self.center_x + (self.window.width / 2) * self.zoom_scale
        min_y = self.center_y - (self.window.height / 2) * self.zoom_scale
        max_y = self.center_y + (self.window.height / 2) * self.zoom_scale
        pyglet.gl.glOrtho(min_x, max_x, min_y, max_y, -1, 1)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()

        for terrain, vertex_list in terrains.items():
            if vertex_list:
                pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
                for i in range(0, len(vertex_list), 8):
                    if i + 7 >= len(vertex_list):
                        break
                    terrain_color = _TERRAIN_DICT[terrain]['color']
                    r, g, b = tuple(map(lambda x: x / 255.0, terrain_color))
                    pyglet.gl.glColor3f(r, g, b)
                    pyglet.gl.glVertex2f(vertex_list[i], vertex_list[i + 1])
                    pyglet.gl.glVertex2f(vertex_list[i + 2], vertex_list[i + 3])
                    pyglet.gl.glVertex2f(vertex_list[i + 4], vertex_list[i + 5])
                    pyglet.gl.glVertex2f(vertex_list[i + 6], vertex_list[i + 7])
                pyglet.gl.glEnd()

        # Draw the character
        pos = self.character._position
        x, y = pos[0], pos[1]
        verts = self.calculate_vertices(x, y)
        pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
        pyglet.gl.glColor3f(1, 0, 0)
        pyglet.gl.glVertex2f(verts[0], verts[1])
        pyglet.gl.glVertex2f(verts[2], verts[3])
        pyglet.gl.glVertex2f(verts[4], verts[5])
        pyglet.gl.glVertex2f(verts[6], verts[7])
        pyglet.gl.glEnd()

        # Draw the path as a series of green squares
        if self.character._traveling:
            for cell in self.character._path:
                c = self.board.cells[cell]
                verts = self.calculate_vertices(c.x, c.y)
                pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
                pyglet.gl.glColor3f(0, 1, 0)
                pyglet.gl.glVertex2f(verts[0], verts[1])
                pyglet.gl.glVertex2f(verts[2], verts[3])
                pyglet.gl.glVertex2f(verts[4], verts[5])
                pyglet.gl.glVertex2f(verts[6], verts[7])
                pyglet.gl.glEnd()

            # Draw the enemy as a yellow square
        pos = self.enemy._position
        x, y = pos[0], pos[1]
        verts = self.calculate_vertices(x, y)
        pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
        pyglet.gl.glColor3f(1, 1, 0)
        pyglet.gl.glVertex2f(verts[0], verts[1])
        pyglet.gl.glVertex2f(verts[2], verts[3])
        pyglet.gl.glVertex2f(verts[4], verts[5])
        pyglet.gl.glVertex2f(verts[6], verts[7])
        pyglet.gl.glEnd()

        if self.enemy._traveling:
            for cell in self.enemy._path:
                c = self.board.cells[cell]
                verts = self.calculate_vertices(c.x, c.y)
                pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
                pyglet.gl.glColor3f(0, 1, 0)
                pyglet.gl.glVertex2f(verts[0], verts[1])
                pyglet.gl.glVertex2f(verts[2], verts[3])
                pyglet.gl.glVertex2f(verts[4], verts[5])
                pyglet.gl.glVertex2f(verts[6], verts[7])
                pyglet.gl.glEnd()

        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glPopMatrix()
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)

    def refresh(self, dt):
        self.update_center()
        self.update_board_edges()
        self.character._update()
        if self.turn_manager.current_actor == self.enemy:
            self.enemy_turn()
        self.enemy._update()
        if self.transitioning:
            self._transition_animation()

    def render(self):
        self.draw_objects()
        if self.transitioning:
            self.screen_sprite.draw()

        # self.draw_character()
