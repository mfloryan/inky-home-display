from PIL import Image, ImageFont, ImageDraw, features
from inky.auto import auto
from datetime import datetime
import locale

def draw_energy_price_graph(draw, colours, hourlyPriceSeries):

    minDim = (20, 60)
    maxDim = (380, 280)
    draw.rectangle([minDim, maxDim], outline=colours[0])

    maxHourlyPrice = max(hourlyPriceSeries)
    minHourlyPrice = min(hourlyPriceSeries)
    dY = maxDim[1] - minDim[1] - 2
    dX = maxDim[0] - minDim[0]
    barW = round(dX / len(hourlyPriceSeries))

    for index, hourlyPrice in enumerate(hourlyPriceSeries):
        barLeft = (barW * index + minDim[0]) + 2
        barRight = (barW * (index +1 ) + minDim[0]) - 2
        barBottom = maxDim[1]
        barTop = maxDim[1] - round(dY * (hourlyPrice / maxHourlyPrice)) 
        if (datetime.now().hour == index):
            draw.rectangle([barLeft-2, minDim[1]+1, barRight+2, barBottom-1], fill=colours[1])

        draw.rectangle([barLeft, barTop, barRight, barBottom], fill=colours[0])
    
    font = ImageFont.load('/usr/share/fonts/X11/misc/ter-u12b_unicode.pil')
    draw.text( (20,40), "min: {0} SEK".format(minHourlyPrice), font = font, fill=colours[0] )
    draw.text( (130, 40), "now: {0} SEK".format(hourlyPriceSeries[datetime.now().hour]), font = font, fill=colours[0] )
    draw.text( (240, 40), "max: {0} SEK".format(maxHourlyPrice), font = font, fill=colours[0] )


def generate_content(draw, data, colours):
    locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

    font22 = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", 22)
    draw.text((10, 10), datetime.now().strftime('%A %d %B %Y'), font = font22, fill=colours[0])

    draw_energy_price_graph(draw, colours, data['energy_prices'])

    locale.setlocale(locale.LC_ALL, "en_GB.utf8")
    font = ImageFont.load('/usr/share/fonts/X11/misc/ter-u12n_unicode.pil')
    now_text = "Updated: " + datetime.now().strftime('%c')
    now_size = draw.textsize(now_text, font=font)
    draw.text((400 - now_size[0], 300 - now_size[1]), now_text, font = font, fill=colours[1])

def display(data):
    
    inky_display = None
    try:
        inky_display = auto()
        print("INKY wHat display:", inky_display.colour)
    except RuntimeError as e:
        print("No INKY display found, using file output instead")

    if inky_display is None:
        img = Image.new("P", size = (400, 300), color = (255,255,255))
        draw = ImageDraw.Draw(img)
        colours = ((0,0,0),(220,220,0),(255,255,255))
    else:
        img = Image.new("P", inky_display.resolution)
        draw = ImageDraw.Draw(img)
        colours = (inky_display.BLACK, inky_display.YELLOW, inky_display.WHITE)

    generate_content(draw, data, colours)

    if inky_display is None:
        img.save("img/test.png", format = "PNG")
    else:
        inky_display.set_border(inky_display.WHITE)
        inky_display.set_image(img)
        inky_display.show()
