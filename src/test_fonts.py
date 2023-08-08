from PIL import Image, ImageFont, ImageDraw, features
from datetime import datetime

def test_fonts():

    print(features.get_supported())

    # sensors = { 'Master Bedroom' : ,
    #             'Garage' :  ,
    #             'Attic' : ,}

    img = Image.new("1", size = (400, 300), color = 1)
    draw = ImageDraw.Draw(img)

    x = 0
    for i in [12, 14, 16, 18]:
        font = ImageFont.load(f"/usr/share/fonts/X11/misc/ter-u{i}n_iso-8859-1.pil")
        draw.text((10, x), "The quick brown fox jumps over the lazy dog " + i, font=font)
        x += i

    font32b = ImageFont.load("/usr/share/fonts/X11/misc/ter-u32b_iso-8859-1.pil")
    draw.text((10, 92), "Hello Bold ºC", font=font32b)

    font32 = ImageFont.load("/usr/share/fonts/X11/misc/ter-u32n_iso-8859-1.pil")
    draw.text((10, 60), "Hello Regular º", font=font32)

    font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf", 20)
    draw.text((100, 140), "world in Ubuntu Mono ºC", font=font)

    font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", 20)
    draw.text((100, 160), "world in Ubuntu ºC", font=font)

    font = ImageFont.truetype("/usr/share/fonts/truetype/oxygen/OxygenMono-Regular.ttf", 20)
    draw.text((100, 180), "Oxygen Mono ºC", font=font)

    font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 20)
    draw.text((100, 200), "Roboto Regular ºC", font=font)

    draw.line([(0,0), (100,0), (0, 100)], width=1, fill=0)

    for i in range(255):
        img.putpixel((i,120), i)

    font = ImageFont.load('/usr/share/fonts/X11/misc/ter-u12n_iso-8859-1.pil')
    now_text = "Updated: " + datetime.now().strftime('%c')
    now_size = draw.textsize(now_text, font=font)
    draw.text((400 - now_size[0], 300 - now_size[1]), now_text, font = font )
    
    img.save("img/fonts.png", format = "PNG")
