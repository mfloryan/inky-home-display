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
    WeatherViewData,
    WeatherWidget,
)


def generate_content(draw, data, colours):
    font_loader = FontLoader()

    header_widget = HeaderWidget(
        Rectangle(4, 0, 396, 25), font_loader, data["current_time"]
    )
    translated_draw = TranslatedDraw(
        draw, header_widget.bounds.x, header_widget.bounds.y
    )
    header_widget.render(translated_draw, colours)

    locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

    if data["energy_prices"]:
        price_data = EnergyPriceData(
            day_prices=data["energy_prices"],
            current_quarter=(data["current_time"].hour * 4)
            + (data["current_time"].minute // 15),
        )

        num_bars = len(data["energy_prices"])
        bar_width = 1
        bar_spacing = 1
        graph_width = (num_bars * (bar_width + bar_spacing)) + 2
        energy_price_graph_widget = EnergyPriceGraphWidget(
            Rectangle(6, 60, graph_width, 200), price_data
        )
        translated_draw = TranslatedDraw(
            draw, energy_price_graph_widget.bounds.x, energy_price_graph_widget.bounds.y
        )
        energy_price_graph_widget.render(translated_draw, colours)

        price_labels_widget = EnergyPriceLabelsWidget(
            Rectangle(10, 28, 260, 30), font_loader, price_data
        )
        translated_draw = TranslatedDraw(
            draw, price_labels_widget.bounds.x, price_labels_widget.bounds.y
        )
        price_labels_widget.render(translated_draw, colours)

    if data["energy_stats"]:
        energy_data = EnergyData(
            production=data["energy_stats"]["production"],
            consumption=data["energy_stats"]["consumption"],
            profit=data["energy_stats"]["profit"],
            cost=data["energy_stats"]["cost"],
        )
        energy_stats_widget = EnergyStatsWidget(
            Rectangle(270, 28, 400 - 270, 100), font_loader, energy_data
        )
        translated_draw = TranslatedDraw(
            draw, energy_stats_widget.bounds.x, energy_stats_widget.bounds.y
        )
        energy_stats_widget.render(translated_draw, colours)

    if data["weather"]:
        weather_view_data = WeatherViewData(
            name=data["weather"]["name"],
            sunrise=data["weather"]["sunrise"],
            sunset=data["weather"]["sunset"],
            now_temp=data["weather"]["now"]["temp"],
            forecast=[
                ForecastItem(
                    time=forecast["time"],
                    temp=forecast["temp"],
                    weather=forecast["weather"]
                )
                for forecast in data["weather"]["forecast"]
            ]
        )
        weather_widget = WeatherWidget(
            Rectangle(280, 6, 120, 200), font_loader, weather_view_data
        )
        translated_draw = TranslatedDraw(
            draw, weather_widget.bounds.x, weather_widget.bounds.y
        )
        weather_widget.render(translated_draw, colours)

    footer_widget = FooterWidget(
        Rectangle(200, 287, 200, 13), font_loader, data["current_time"]
    )
    translated_draw = TranslatedDraw(
        draw, footer_widget.bounds.x, footer_widget.bounds.y
    )
    footer_widget.render(translated_draw, colours)


def display(data, prefer_inky=True, png_output_path="img/test.png"):
    backend = create_backend(prefer_inky, png_output_path)

    img = backend.create_image()
    draw = ImageDraw.Draw(img)
    colours = backend.colors

    generate_content(draw, data, colours)
    backend.show(img)
