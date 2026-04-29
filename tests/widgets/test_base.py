from unittest.mock import MagicMock

from PIL import Image

from widgets.base import TranslatedDraw


class TestTranslatedDrawPasteImage:
    def test_paste_image_translates_xy_by_offset(self):
        mock_img = MagicMock()
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_img, mock_draw, offset_x=10, offset_y=20)

        icon = Image.new("RGB", (16, 16), (255, 255, 255))
        translated.paste_image(icon, (5, 5))

        mock_img.paste.assert_called_once_with(icon, (15, 25))

    def test_paste_image_at_origin_with_zero_offset(self):
        mock_img = MagicMock()
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_img, mock_draw, offset_x=0, offset_y=0)

        icon = Image.new("RGB", (32, 32), (255, 255, 255))
        translated.paste_image(icon, (0, 44))

        mock_img.paste.assert_called_once_with(icon, (0, 44))

    def test_existing_text_method_still_works(self):
        mock_img = MagicMock()
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_img, mock_draw, offset_x=5, offset_y=10)

        translated.text((0, 0), "hello", fill=(0, 0, 0))

        mock_draw.text.assert_called_once_with((5, 10), "hello", fill=(0, 0, 0))
