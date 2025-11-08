import locale
from PIL import ImageDraw

from display_backend import create_backend
from fonts import FontLoader
from widgets import (
    EnergyData,
    EnergyPriceData,
    EnergyPriceGraphWidget,
    EnergyPriceLabelsWidget,
    EnergyStatsWidget,
    FooterWidget,
    ForecastItem,
    HeaderWidget,
    Rectangle,
    TranslatedDraw,
    TransportWidget,
    WeatherViewData,
    WeatherWidget,
)


LAYOUT = {
    "header": Rectangle(4, 0, 396, 25),
    "price_labels": Rectangle(10, 28, 260, 30),
    "energy_stats": Rectangle(200, 256, 0, 65),
    "energy_graph": Rectangle(6, 60, 194, 194),
    "transport": Rectangle(202, 28, 76, 259),
    "weather": Rectangle(280, 6, 120, 200),
    "footer": Rectangle(200, 287, 200, 13),
}


def render_widget(widget, draw, colours):
    translated_draw = TranslatedDraw(draw, widget.bounds.x, widget.bounds.y)
    widget.render(translated_draw, colours)


def create_header_widget(bounds, data, font_loader):
    return [HeaderWidget(bounds, font_loader, data["current_time"])]


def create_energy_price_widgets(graph_bounds, labels_bounds, data, font_loader):
    if not data["energy_prices"]:
        return []

    price_data = EnergyPriceData(
        day_prices=data["energy_prices"],
        current_quarter=(data["current_time"].hour * 4)
        + (data["current_time"].minute // 15),
    )

    return [
        EnergyPriceGraphWidget(graph_bounds, price_data),
        EnergyPriceLabelsWidget(labels_bounds, font_loader, price_data),
    ]


def create_energy_stats_widget(bounds, data, font_loader):
    if not data["energy_stats"]:
        return []

    energy_data = EnergyData(
        production=data["energy_stats"]["production"],
        consumption=data["energy_stats"]["consumption"],
        profit=data["energy_stats"]["profit"],
        cost=data["energy_stats"]["cost"],
    )

    return [EnergyStatsWidget(bounds, font_loader, energy_data)]


def create_weather_widget(bounds, data, font_loader):
    if not data["weather"]:
        return []

    weather_view_data = WeatherViewData(
        name=data["weather"]["name"],
        sunrise=data["weather"]["sunrise"],
        sunset=data["weather"]["sunset"],
        now_temp=data["weather"]["now"]["temp"],
        forecast=[
            ForecastItem(
                time=forecast["time"], temp=forecast["temp"], weather=forecast["weather"]
            )
            for forecast in data["weather"]["forecast"]
        ],
    )

    return [WeatherWidget(bounds, font_loader, weather_view_data)]


def create_footer_widget(bounds, data, font_loader):
    return [FooterWidget(bounds, font_loader, data["current_time"])]


def create_transport_widget(bounds, data, font_loader):
    return [TransportWidget(bounds, font_loader)]


def generate_content(draw, data, colours):
    font_loader = FontLoader()
    locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

    widgets = []
    widgets.extend(create_header_widget(LAYOUT["header"], data, font_loader))
    widgets.extend(
        create_energy_price_widgets(
            LAYOUT["energy_graph"], LAYOUT["price_labels"], data, font_loader
        )
    )
    widgets.extend(create_energy_stats_widget(LAYOUT["energy_stats"], data, font_loader))
    widgets.extend(create_transport_widget(LAYOUT["transport"], data, font_loader))
    widgets.extend(create_weather_widget(LAYOUT["weather"], data, font_loader))
    widgets.extend(create_footer_widget(LAYOUT["footer"], data, font_loader))

    for widget in widgets:
        render_widget(widget, draw, colours)


def display(data, prefer_inky=True, png_output_path="img/test.png"):
    backend = create_backend(prefer_inky, png_output_path)

    img = backend.create_image()
    draw = ImageDraw.Draw(img)
    colours = backend.colors

    generate_content(draw, data, colours)
    backend.show(img)
