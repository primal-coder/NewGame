from abc import ABC
from typing import Optional

import pyglet.image
import pyglet.sprite

assetPath = "build/assets/"
playerAssets = f"{assetPath}aplayer/"
heroAssets = f"{assetPath}ahero/"


class StateMachine:
    def __init__(
            self,
            controller: Optional[object],
            rows: Optional[int] = None,
            cols: Optional[int] = None,
            frame_size: Optional[tuple[int, int]] = None,
            total_frames: Optional[int] = None,
            time_scale: Optional[float] = None,
            state_sheet: Optional[object] = None,
            verbose: Optional[bool] = None,
            _loop: Optional[bool] = None,
            static: Optional[bool] = None,
            *args, **kwargs
    ):
        self.frame_adj = None
        self.loop = None
        self.texture_grid = None
        self.frames = None
        self.controller = controller
        self.str_path = self.__class__.__name__.lower()
        self.path = f"{self.controller.path}{self.str_path}.png"
        self.age = 0
        self.facing = self.controller.facing
        self.action = self.controller.active_state
        self._loop = _loop if _loop is not None else True
        self.frame_size = frame_size if frame_size is not None else (32, 32)
        self.frame_width = self.frame_size[0]
        self.frame_height = self.frame_size[1]
        self.row_count = rows
        self.col_count = cols
        self.total_frames = total_frames
        self.frame_mod = self.total_frames
        self.time_scale = time_scale if time_scale is not None else 1.0
        self.state_sheet = state_sheet if state_sheet is not None else (
            self.load_state_sheet(
                self.path,
                self.row_count,
                self.col_count,
                self.frame_width,
                self.frame_height
            )
        )
        self.frame_ = 0
        self.verbose = verbose if verbose is not None else True
        self.label = None
        self.static = static if static is not None else False
        if self.static:
            self.__setattr__("staticx", self.controller.x)
            self.__setattr__("staticy", self.controller.y)
        self.sprite = pyglet.sprite.Sprite(self.frames[self.frame_].image, controller.x, controller.y - 32)
        self.attach_label()

    def attach_label(self):
        self.__setattr__("label", pyglet.text.Label(str(self.__class__.__name__), font_name="Arial", font_size=10,
                                                    x=self.controller.x + 16, y=self.controller.y - 16,
                                                    anchor_x="center", anchor_y="center"))

    def load_state_sheet(self, path, rows, cols, frame_width, frame_height):
        state_sheet = StateSheet(path, rows, cols, frame_width, frame_height)
        self.__setattr__("texture_grid", StateTexture(state_sheet))
        self.__setattr__("loop", StateLoop(state_sheet, self.time_scale))
        self.__setattr__("_frames", self.texture_grid[0])
        self.__setattr__("frames", self.loop.frames)
        return state_sheet

    def _cln_(self):
        self.sprite.delete()

    def flip(self):
        if self.age % (int(60 * self.time_scale)) == 0:
            self.frame_ += 1

    def adjust_frame_mod(self, new):
        if self.frame_mod != new:
            self.frame_mod = new

    def frame_modulo(self):
        self.frame_ %= self.frame_mod

    def forward(self):
        if self._loop:
            self.flip()
        else:
            if self.frame_ != self.total_frames - 1:
                self.flip()

    def set_adj(self):
        if self.facing < 0:
            self.__setattr__("frame_adj", self.frames[self.frame_].image.width)
        else:
            self.__setattr__("frame_adj", 0)

    def set_frame(self, frame):
        if not self.static:
            self.sprite = pyglet.sprite.Sprite(frame, self.controller.x, self.controller.y)
            self.sprite.update(x=self.controller.x + self.frame_adj, scale_x=self.facing)

    def refresh(self):
        self._cln_()
        self.facing = self.controller.facing
        self.action = self.controller.action
        self.forward()
        self.frame_modulo()
        self.set_adj()

    def get_frame(self):
        return self.frames[self.frame_].image

    def update(self):
        self.age += 1
        self.refresh()
        self.set_frame(self.get_frame())

    def draw(self):
        self.sprite.draw()


class StateLoop:
    """
        Generate an animation object from our sheet/texture object

    """

    def __init__(
            self,
            sheet=None,
            duration=None
    ):
        self.animation = pyglet.image.Animation.from_image_sequence(sheet, duration)
        self.frames = self.animation.frames


class StateTexture(pyglet.image.TextureGrid):
    """
        Generate a texture grid object from our sheet object
    """

    def _get_item_height(self):
        pass

    def _get_item_width(self):
        pass

    def __init__(self, sheet=None):
        super(StateTexture, self).__init__(sheet)


class StateSheet(pyglet.image.ImageGrid, ABC):
    """ 
        Generate a grid of images from a sprite sheet
    """

    def __init__(
            self,
            path: str = None,
            row_count: int = None,
            col_count: int = None,
            frame_width: int = None,
            frame_height: int = None
    ):
        self._img = pyglet.image.load(path)
        self._rows = row_count
        self._columns = col_count
        self.frame_width = frame_width if frame_width is not None else self._img.width // self._columns
        self.frame_height = frame_height if frame_height is not None else self._img.height // self._rows
        self.start_ = 0
        super(StateSheet, self).__init__(self._img, self._rows, self._columns, self.frame_width, self.frame_height)


class PIdle(StateMachine):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, 1, 4, (256, 256), 4, .33, *args, **kwargs)


class PRun(StateMachine):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, 2, 8, (128, 128), 16, .055, *args, **kwargs)

    def flip(self):
        super().flip()

    def update(self):
        super().update()

    def draw(self):
        super().draw()


class PJump(StateMachine):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, 1, 4, (64, 64), 4, .22, *args, **kwargs)

    def forward(self):
        if self.frame_ == 2:
            self._loop = False
        super().forward()


class PDust(StateMachine):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, 1, 4, (64, 64), 4, 0.45, verbose=False, _loop=False, static=True, *args, **kwargs)


class Actions(StateMachine):
    def __init__(self, controller):
        super(Actions, self).__init__(controller, 4, 4, (128, 128), 10, .53)


class AHeroStates(StateMachine):
    def __init__(self, controller):
        super(AHeroStates, self).__init__(controller, 1, 3, (90, 100), 3, .75)

    def blink(self):
        self.adjust_frame_mod(3)
        self.frame_ = 2

    def update(self):
        super().update()
        if self.age % 180 in list(range(0, 10)):
            self.blink()
        else:
            self.adjust_frame_mod(2)


class NewPlayerIdle(StateMachine):
    def __init__(self, controller):
        super(NewPlayerIdle, self).__init__(controller, 1, 4, (128, 128), 5, .22)
        self.adjust_frame_mod(4)

    def update(self):
        super().update()
        self.sprite.scale_x = 1


class NewPlayerRun(StateMachine):
    def __init__(self, controller):
        super(NewPlayerRun, self).__init__(controller, 1, 4, (128, 128), 4, .145)

    def update(self):
        super().update()
        self.sprite.scale_x = 1


class HorseRun(StateMachine):
    def __init__(self, controller):
        super(HorseRun, self).__init__(controller, 2, 6, (256, 160), 12, .35)
