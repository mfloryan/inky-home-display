import math
import locale
from PIL import ImageDraw
from display_backend import create_backend
from fonts import (
    ubuntu_regular,
    terminus_bold_16, terminus_regular_12, terminus_bold_14, terminus_bold_22
)

def draw_energy_price_graph(draw, colours, day_hourly_prices, current_time):
    min_dim = {'x': 6, 'y': 60}
    max_dim = {'x': 270, 'y': 284}
    draw.rectangle([min_dim['x'], min_dim['y'], max_dim['x'], max_dim['y']], outline=colours[0])

    hourly_price_max = max(day_hourly_prices)
    hourly_price_min = min(day_hourly_prices)

    _draw_price_reference_lines(draw, colours, hourly_price_max, min_dim, max_dim)
    _draw_hourly_price_bars(draw, colours, day_hourly_prices, min_dim, max_dim, current_time)
    _draw_price_labels(draw, colours, day_hourly_prices, hourly_price_min, hourly_price_max, current_time)


def _draw_price_reference_lines(draw, colours, hourly_price_max, min_dim, max_dim):
    dy = max_dim['y'] - min_dim['y'] - 2
    if hourly_price_max > 1.0:
        highest_full_sek = math.floor(hourly_price_max)
        one_sek_step = round(((highest_full_sek * dy) / hourly_price_max) / highest_full_sek)

        for y in range(highest_full_sek):
            for x in range(min_dim['x'] + 1, max_dim['x']):
                if x % 2 == 0:
                    draw.point([x, max_dim['y'] - (one_sek_step * (y + 1))], fill=colours[0])


def _draw_hourly_price_bars(draw, colours, day_hourly_prices, min_dim, max_dim, current_time):
    dy = max_dim['y'] - min_dim['y'] - 2
    dx = max_dim['x'] - min_dim['x']
    bar_width = round(dx / len(day_hourly_prices))
    hourly_price_max = max(day_hourly_prices)
    hourly_price_min = min(day_hourly_prices)
    max_abs_price = max(abs(hourly_price_max), abs(hourly_price_min), 1.0)

    for hour, hourly_price in enumerate(day_hourly_prices):
        bar_left = (bar_width * hour + min_dim['x']) + 2
        bar_right = (bar_width * (hour + 1) + min_dim['x']) - 2

        if hourly_price >= 0:
            bar_top = max_dim['y'] - round(dy * (hourly_price / max_abs_price))
            bar_bottom = max_dim['y']
        else:
            bar_top = min_dim['y']
            bar_bottom = min_dim['y'] + round(dy * (abs(hourly_price) / max_abs_price))

        if current_time.hour == hour:
            draw.rectangle([bar_left - 2, min_dim['y'] + 1,
                            bar_right + 2, max_dim['y'] - 1], fill=colours[1])

        draw.rectangle([bar_left, bar_top, bar_right, bar_bottom], fill=colours[0])


def _draw_price_labels(draw, colours, day_hourly_prices, hourly_price_min, hourly_price_max, current_time):
    font_bold = terminus_bold_16()
    font = terminus_regular_12()

    price_range_text = f"{round(hourly_price_min, 2)} -- {round(hourly_price_max, 2)} SEK"
    draw.text((10, 28), price_range_text, font=font, fill=colours[0])

    now_price_baseline = 42
    now_price_left = 10
    now_price_text = f"now: {round(day_hourly_prices[current_time.hour], 2)} SEK"
    draw.rectangle(
        [(now_price_left - 2, now_price_baseline - 1),
         (now_price_left - 2 + draw.textlength(now_price_text, font=font_bold) + 2, now_price_baseline + 13)],
        outline=colours[1], width=1)
    draw.text((now_price_left, now_price_baseline), now_price_text, font=font_bold, fill=colours[0])


def draw_energy_stats(draw, colours, data):
    font = ubuntu_regular(11)
    production_text = f"do sieci {round(data['production'], 2)} kWh {data['profit']:+.2f} SEK"
    consumption_text = f"z sieci {round(data['consumption'], 2)} kWh {(-1) * data['cost']:+.2f} SEK"

    draw.text((270, 28), production_text, font=font, fill=colours[0], anchor="ra")
    draw.text((270, 42), consumption_text, font=font, fill=colours[0], anchor="ra")


def draw_weather(draw, colours, data):
    font_sun = terminus_regular_12()
    font_header = terminus_bold_14()
    font_temp = terminus_bold_22()
    font_label = ubuntu_regular(12)
    temperature_right = 390

    def draw_single_forecast(forecast, y):
        draw.text((280, y), forecast['time'].strftime('%H:%M'), font=font_header, fill=colours[0])
        temp_text = f"{round(forecast['temp'])}°C"
        draw.text((temperature_right - draw.textlength(temp_text, font=font_temp), y - 6), temp_text, font=font_temp,
                  fill=colours[0])
        y += 12
        draw.text((280, y), forecast['weather'], font=font_label, fill=colours[0])
        y += 26
        return y

    draw.text((300, 6), "POGODA", font=font_header, fill=colours[1])
    draw.text((300, 20), data['name'], font=font_label, fill=colours[0])
    draw.ellipse([(286, 36), (297, 47)], fill=colours[1])
    draw.text((300, 36), f"{data['sunrise'].strftime('%H:%M')}-{data['sunset'].strftime('%H:%M')}",
              font=font_sun,
              fill=colours[0])
    temp_text = f"{round(data['now']['temp'], 1)}°C"
    draw.text((temperature_right - draw.textlength(temp_text, font=font_temp), 50), temp_text, font=font_temp,
              fill=colours[0])
    draw.text((280, 55), "teraz:", font=font_label, fill=colours[1])

    forecast_y = 86
    for forecast in data['forecast'][:4]:
        forecast_y = draw_single_forecast(forecast, forecast_y)


def generate_content(draw, data, colours):
    locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

    font22 = ubuntu_regular(22)
    draw.text((4, 0), data['current_time'].strftime(
        '%A %d %B %Y'), font=font22, fill=colours[0])

    if data['energy_prices']:
        draw_energy_price_graph(draw, colours, data['energy_prices'], data['current_time'])

    if data['energy_stats']:
        draw_energy_stats(draw, colours, data['energy_stats'])

    if data['weather']:
        draw_weather(draw, colours, data['weather'])

    locale.setlocale(locale.LC_ALL, "en_GB.utf8")
    font = terminus_regular_12()
    now_text = "Updated: " + data['current_time'].strftime('%c')
    now_size = draw.textbbox((0, 0), now_text, font=font)
    draw.text((400 - now_size[2], 300 - now_size[3]),
              now_text, font=font, fill=colours[1])


def display(data, prefer_inky=True, png_output_path="img/test.png"):
    backend = create_backend(prefer_inky, png_output_path)

    img = backend.create_image()
    draw = ImageDraw.Draw(img)
    colours = backend.colors

    generate_content(draw, data, colours)
    backend.show(img)
