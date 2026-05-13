from unittest.mock import MagicMock

from PIL import Image

from widgets.base import TranslatedDraw


class TestTranslatedDrawBitmap:
    def test_bitmap_translates_xy_by_offset(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=10, offset_y=20)

        icon = Image.new("1", (16, 16), 0)
        translated.bitmap((5, 5), icon, fill=(0, 0, 0))

        mock_draw.bitmap.assert_called_once_with((15, 25), icon, fill=(0, 0, 0))

    def test_bitmap_at_origin_with_zero_offset(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=0, offset_y=0)

        icon = Image.new("1", (32, 32), 0)
        translated.bitmap((0, 44), icon, fill=(0, 0, 0))

        mock_draw.bitmap.assert_called_once_with((0, 44), icon, fill=(0, 0, 0))

    def test_existing_text_method_still_works(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=5, offset_y=10)

        translated.text((0, 0), "hello", fill=(0, 0, 0))

        mock_draw.text.assert_called_once_with((5, 10), "hello", fill=(0, 0, 0))
