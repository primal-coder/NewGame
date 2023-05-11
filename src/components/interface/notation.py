from typing import Optional as _Optional

import pyglet.gui
import pyglet.text as _text
import pyglet.graphics as _graphics

import contextlib


class Label(_text.Label):
    def __init__(
            self,
            scene=None,
            x: int = None,
            y: int = None,
            text: str = None,
            size=None,
            batch_=None,
            *args, **kwargs
    ):
        self.scene = scene
        self.batch_ = batch_ if batch_ is not None else _graphics.Batch()
        super(Label, self).__init__(font_name="terminal", font_size=size, batch=self.batch_, color=(255, 255, 255, 255))
        self.x = x
        self.y = y
        self.document.insert_text(0, text)

    def rewrite(self, new):
        self.document.delete_text(0, len(self.text))
        self.document.insert_text(0, new)


class Message(_text.Label):
    def __init__(
            self,
            parent = None,
            x: int = None,
            y: int = None,
            text: str = None,
            batch=None,
            expiration: _Optional[int] = None,
            *args, **kwargs
    ):
        self.parent = parent
        self.expiration = expiration if expiration is not None else 0
        self.age = 0
        self.active = True
        super(Message, self).__init__(text, "terminal", 10, True, False, False, (255, 255, 255, 255), x, y, batch=batch)

    def draw(self):
        if self.active:
            super().draw()

    def rewrite(self, new):
        self.document.delete_text(0, len(self.text))
        self.document.insert_text(0, new)

    def update(self):
        if self.active:
            self.age += 1
            if self.age >= self.expiration != 0:
                self.active = False
        else:
            self.document.delete_text(0, len(self.text))
            self.end_update()
            self.delete()
            self.parent.event_labels.pop(self.parent.event_labels.index(self))
            del self

    def __del__(self):
        self = None

    @classmethod
    @contextlib.contextmanager
    def context(cls, parent, x, y, text, batch, expiration):
        message = cls(parent, x, y, text, batch, expiration)
        try:
            yield message
        finally:
            del message


class DynamicLabel(Message):
    def __init__(
            self,
            parent=None,
            attr: str = None,
            x: int = None,
            y: int = None,
            expiration: _Optional[int] = None,
            index: _Optional[int] = None,
            batch=None
    ):
        self.parent = parent
        self.attr = attr
        self.data = str(self.parent.__getattribute__(self.attr))
        self.index = index
        self.strings = [f"{self.attr}", f"{self.data}", f"{self.attr} : {self.data}", f"{self.data} : {self.attr}"]
        self.string = self.strings[self.index]
        super(DynamicLabel, self).__init__(self.parent, x, y, self.string)

    def update(self):
        super().update()
        self.data = str(self.parent.__getattribute__(self.attr))
        self.strings = [f"{self.attr}", f"{self.data}", f"{self.attr} : {self.data}", f"{self.data} : {self.attr}"]
        self.string = self.strings[self.index]
        self.rewrite(f"{self.string}")

