import math
import locale
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from inky.auto import auto


def draw_energy_price_graph(draw, colours, day_hourly_prices):

    min_dim = (6, 60)
    max_dim = (390, 284)
    draw.rectangle([min_dim, max_dim], outline=colours[0])

    hourly_price_max = max(day_hourly_prices)
    hourly_price_min = min(day_hourly_prices)
    dy = max_dim[1] - min_dim[1] - 2
    dx = max_dim[0] - min_dim[0]
    bar_width = round(dx / len(day_hourly_prices))

    if hourly_price_max > 1.0:
        highest_full_sek = math.floor(hourly_price_max)
        one_sek_step = round(
            ((highest_full_sek * dy) / hourly_price_max) / highest_full_sek)

        for y in range(highest_full_sek):
            for x in range(min_dim[0]+1, max_dim[0]):
                if x % 2 == 0:
                    draw.point(
                        [x, max_dim[1]-(one_sek_step * (y+1))], fill=colours[0])

    # scale up to max value or 1 for small daily values
    x_axis_max = max(hourly_price_max, 1)
    for hour, hourly_price in enumerate(day_hourly_prices):
        bar_left = (bar_width * hour + min_dim[0]) + 2
        bar_right = (bar_width * (hour + 1) + min_dim[0]) - 2
        bar_bottom = max_dim[1]
        bar_top = max_dim[1] - round(dy * (hourly_price / x_axis_max))
        if datetime.now().hour == hour:
            draw.rectangle([bar_left-2, min_dim[1]+1,
                           bar_right+2, bar_bottom-1], fill=colours[1])

        draw.rectangle([bar_left, bar_top, bar_right,
                       bar_bottom], fill=colours[0])

    font_bold = ImageFont.load(
        '/usr/share/fonts/X11/misc/ter-u16b_unicode.pil')
    font = ImageFont.load('/usr/share/fonts/X11/misc/ter-u12n_unicode.pil')

    price_range_text = f"{round(hourly_price_min, 2)} -- {round(hourly_price_max, 2)} SEK"
    now_price_text = f"now: {round(day_hourly_prices[datetime.now().hour], 2)} SEK"
    draw.line(
        (10, 48, 10 + draw.textlength(now_price_text, font=font_bold), 48),
        fill=colours[1], width=4)

    draw.text((10, 26), price_range_text, font=font,
              fill=colours[0], anchor="ms")
    draw.text((10, 38), now_price_text, font=font_bold, fill=colours[0])


def generate_content(draw, data, colours):
    locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

    font22 = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", 22)
    draw.text((4, 0), datetime.now().strftime(
        '%A %d %B %Y'), font=font22, fill=colours[0])

    draw_energy_price_graph(draw, colours, data['energy_prices'])

    locale.setlocale(locale.LC_ALL, "en_GB.utf8")
    font = ImageFont.load('/usr/share/fonts/X11/misc/ter-u12n_unicode.pil')
    now_text = "Updated: " + datetime.now().strftime('%c')
    now_size = draw.textsize(now_text, font=font)
    draw.text((400 - now_size[0], 300 - now_size[1]),
              now_text, font=font, fill=colours[1])


def display(data):
    inky_display = None
    try:
        inky_display = auto()
        print("INKY wHat display:", inky_display.colour)
    except RuntimeError:
        print("No INKY display found, using file output instead")

    if inky_display is None:
        img = Image.new("P", size=(400, 300), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        colours = ((0, 0, 0), (220, 220, 0), (255, 255, 255))
    else:
        img = Image.new("P", inky_display.resolution)
        draw = ImageDraw.Draw(img)
        colours = (inky_display.BLACK, inky_display.YELLOW, inky_display.WHITE)

    generate_content(draw, data, colours)

    if inky_display is None:
        img.save("img/test.png", format="PNG")
    else:
        inky_display.set_border(inky_display.WHITE)
        inky_display.set_image(img)
        inky_display.show()
