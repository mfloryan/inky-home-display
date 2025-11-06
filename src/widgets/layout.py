import datetime
import locale

from fonts import FontLoader
from widgets.base import DrawProtocol, Rectangle, Widget


class HeaderWidget(Widget):
    def __init__(
        self,
        bounds: Rectangle,
        font_loader: FontLoader,
        current_time: datetime.datetime,
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.current_time = current_time

    def render(self, draw: DrawProtocol, colours: list) -> None:
        locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
        font = self.font_loader.ubuntu_regular(22)
        date_text = self.current_time.strftime("%A %d %B %Y")
        draw.text((0, 0), date_text, font=font, fill=colours[0])


class FooterWidget(Widget):
    def __init__(
        self,
        bounds: Rectangle,
        font_loader: FontLoader,
        current_time: datetime.datetime,
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.current_time = current_time

    def render(self, draw: DrawProtocol, colours: list) -> None:
        locale.setlocale(locale.LC_ALL, "en_GB.utf8")
        font = self.font_loader.terminus_regular_12()
        now_text = "Updated: " + self.current_time.strftime("%c")
        now_size = draw.textbbox((0, 0), now_text, font=font)

        x = self.bounds.width - now_size[2]
        y = self.bounds.height - now_size[3]
        draw.text((x, y), now_text, font=font, fill=colours[1])
