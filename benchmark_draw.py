import time
from PIL import Image, ImageDraw

def draw_old(draw, width, height, highest_full_sek, one_sek_step, colour):
    for y in range(highest_full_sek):
        for x in range(1, width):
            if x % 2 == 0:
                draw.point(
                    [x, height - (one_sek_step * (y + 1))],
                    fill=colour,
                )

def draw_new(draw, width, height, highest_full_sek, one_sek_step, colour):
    points = [
        (x, height - (one_sek_step * (y + 1)))
        for y in range(highest_full_sek)
        for x in range(2, width, 2)
    ]
    if points:
        draw.point(points, fill=colour)


width = 800
height = 480
highest_full_sek = 10
one_sek_step = 20

img1 = Image.new('RGB', (width, height), color = 'white')
draw1 = ImageDraw.Draw(img1)

start = time.perf_counter()
for _ in range(100):
    draw_old(draw1, width, height, highest_full_sek, one_sek_step, (0, 0, 0))
print(f"Old method: {time.perf_counter() - start:.5f}s")

img2 = Image.new('RGB', (width, height), color = 'white')
draw2 = ImageDraw.Draw(img2)

start = time.perf_counter()
for _ in range(100):
    draw_new(draw2, width, height, highest_full_sek, one_sek_step, (0, 0, 0))
print(f"New method: {time.perf_counter() - start:.5f}s")
