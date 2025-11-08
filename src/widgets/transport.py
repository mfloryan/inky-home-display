from fonts import FontLoader
from widgets.base import DrawProtocol, Rectangle, Widget


class TransportWidget(Widget):
    def __init__(self, bounds: Rectangle, font_loader: FontLoader):
        super().__init__(bounds)
        self.font_loader = font_loader

    def render(self, draw: DrawProtocol, colours: list) -> None:
        draw.rectangle(
            [0, 0, self.bounds.width - 1, self.bounds.height - 1], outline=colours[1]
        )

        font_header = self.font_loader.terminus_bold_14()
        draw.text((2, 2), "TRANSPORT", font=font_header, fill=colours[1])
