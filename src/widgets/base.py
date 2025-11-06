from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Rectangle:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


class DrawProtocol(Protocol):
    def text(self, xy, text, **kwargs): ...
    def rectangle(self, xy, **kwargs): ...
    def textlength(self, text, **kwargs) -> float: ...
    def textbbox(self, xy, text, **kwargs) -> tuple[float, float, float, float]: ...
    def point(self, xy, **kwargs): ...
    def ellipse(self, xy, **kwargs): ...


class TranslatedDraw:
    def __init__(self, draw: DrawProtocol, offset_x: int, offset_y: int):
        self.draw = draw
        self.offset_x = offset_x
        self.offset_y = offset_y

    def text(self, xy, text, **kwargs):
        translated_xy = (xy[0] + self.offset_x, xy[1] + self.offset_y)
        return self.draw.text(translated_xy, text, **kwargs)

    def rectangle(self, xy, **kwargs):
        if len(xy) == 4:
            translated_xy = [
                xy[0] + self.offset_x,
                xy[1] + self.offset_y,
                xy[2] + self.offset_x,
                xy[3] + self.offset_y,
            ]
        else:
            translated_xy = [
                (xy[0][0] + self.offset_x, xy[0][1] + self.offset_y),
                (xy[1][0] + self.offset_x, xy[1][1] + self.offset_y),
            ]
        return self.draw.rectangle(translated_xy, **kwargs)

    def textlength(self, text, **kwargs):
        return self.draw.textlength(text, **kwargs)

    def textbbox(self, xy, text, **kwargs):
        return self.draw.textbbox(xy, text, **kwargs)

    def point(self, xy, **kwargs):
        translated_xy = (xy[0] + self.offset_x, xy[1] + self.offset_y)
        return self.draw.point(translated_xy, **kwargs)

    def ellipse(self, xy, **kwargs):
        if len(xy) == 4:
            translated_xy = [
                xy[0] + self.offset_x,
                xy[1] + self.offset_y,
                xy[2] + self.offset_x,
                xy[3] + self.offset_y,
            ]
        else:
            translated_xy = [
                (xy[0][0] + self.offset_x, xy[0][1] + self.offset_y),
                (xy[1][0] + self.offset_x, xy[1][1] + self.offset_y),
            ]
        return self.draw.ellipse(translated_xy, **kwargs)


class Widget(ABC):
    def __init__(self, bounds: Rectangle):
        self.bounds = bounds

    @abstractmethod
    def render(self, draw: DrawProtocol, colours: list) -> None:
        pass
