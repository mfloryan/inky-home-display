from dataclasses import dataclass

from fonts import FontLoader
from widgets.base import DrawProtocol, Rectangle, Widget


@dataclass
class EnergyData:
    production: float
    consumption: float
    profit: float
    cost: float


@dataclass
class EnergyPriceData:
    day_prices: list[float]
    current_quarter: int


class EnergyStatsWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, energy_data: EnergyData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.energy_data = energy_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        font = self.font_loader.ubuntu_regular(11)
        production_text = f"do sieci {round(self.energy_data.production, 2)} kWh {self.energy_data.profit:+.2f} SEK"
        consumption_text = f"z sieci {round(self.energy_data.consumption, 2)} kWh {(-1) * self.energy_data.cost:+.2f} SEK"

        draw.text((0, 0), production_text, font=font, fill=colours[0], anchor="ra")
        draw.text((0, 14), consumption_text, font=font, fill=colours[0], anchor="ra")


class EnergyPriceLabelsWidget(Widget):
    def __init__(
        self, bounds: Rectangle, font_loader: FontLoader, price_data: EnergyPriceData
    ):
        super().__init__(bounds)
        self.font_loader = font_loader
        self.price_data = price_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        price_max = max(self.price_data.day_prices)
        price_min = min(self.price_data.day_prices)

        font_bold = self.font_loader.terminus_bold_16()
        font = self.font_loader.terminus_regular_12()

        price_range_text = f"{round(price_min, 2)} -- {round(price_max, 2)} SEK"
        draw.text((0, 0), price_range_text, font=font, fill=colours[0])

        now_price_baseline = 14
        now_price_left = 0
        now_price_text = f"now: {round(self.price_data.day_prices[self.price_data.current_quarter], 2)} SEK"
        draw.rectangle(
            [
                (now_price_left - 2, now_price_baseline - 1),
                (
                    now_price_left
                    - 2
                    + draw.textlength(now_price_text, font=font_bold)
                    + 2,
                    now_price_baseline + 13,
                ),
            ],
            outline=colours[1],
            width=1,
        )
        draw.text(
            (now_price_left, now_price_baseline),
            now_price_text,
            font=font_bold,
            fill=colours[0],
        )


class EnergyPriceGraphWidget(Widget):
    def __init__(self, bounds: Rectangle, price_data: EnergyPriceData):
        super().__init__(bounds)
        self.price_data = price_data

    def render(self, draw: DrawProtocol, colours: list) -> None:
        draw.rectangle(
            [0, 0, self.bounds.width, self.bounds.height], outline=colours[0]
        )

        price_max = max(self.price_data.day_prices)
        self._draw_reference_lines(draw, colours, price_max)
        self._draw_price_bars(draw, colours)

    def _draw_reference_lines(
        self, draw: DrawProtocol, colours: list, price_max: float
    ) -> None:
        dy = self.bounds.height - 2
        if price_max > 1.0:
            highest_full_sek = int(price_max)
            one_sek_step = round(
                ((highest_full_sek * dy) / price_max) / highest_full_sek
            )

            for y in range(highest_full_sek):
                for x in range(1, self.bounds.width):
                    if x % 2 == 0:
                        draw.point(
                            [x, self.bounds.height - (one_sek_step * (y + 1))],
                            fill=colours[0],
                        )

    def _draw_price_bars(self, draw: DrawProtocol, colours: list) -> None:
        dy = self.bounds.height - 2
        bar_width = 1
        bar_spacing = 1
        price_max = max(self.price_data.day_prices)
        price_min = min(self.price_data.day_prices)
        max_abs_price = max(abs(price_max), abs(price_min), 1.0)

        for index, price in enumerate(self.price_data.day_prices):
            bar_left = (bar_width + bar_spacing) * (index + 1)
            bar_right = bar_left + bar_width - 1

            if price >= 0:
                bar_top = self.bounds.height - round(dy * (price / max_abs_price))
                bar_bottom = self.bounds.height
            else:
                bar_top = 0
                bar_bottom = round(dy * (abs(price) / max_abs_price))

            if self.price_data.current_quarter == index:
                draw.rectangle(
                    [bar_left - 1, 1, bar_right + 1, self.bounds.height - 1],
                    fill=colours[1],
                )

            draw.rectangle([bar_left, bar_top, bar_right, bar_bottom], fill=colours[0])
