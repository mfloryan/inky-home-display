import os

from PIL import Image

OW_TO_XBM = {
    "01d": "sun",
    "01n": "moon",
    "02d": "cloud_sun",
    "02n": "cloud_moon",
    "03d": "cloud",
    "03n": "cloud",
    "04d": "clouds",
    "04n": "clouds",
    "09d": "rain1",
    "09n": "rain1",
    "10d": "rain0_sun",
    "10n": "rain1",
    "11d": "rain_lightning",
    "11n": "rain_lightning",
    "13d": "snow",
    "13n": "snow",
    "50d": "cloud_wind",
    "50n": "cloud_wind",
}

_ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")


def load_icon(ow_code: str, size: int) -> Image.Image:
    name = OW_TO_XBM[ow_code]
    path = os.path.join(_ICONS_DIR, str(size), f"{name}.xbm")
    return Image.open(path)
