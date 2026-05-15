from unittest.mock import MagicMock

from PIL import Image

from widgets.base import Rectangle, TranslatedDraw


class WhenUsingRectangle:
    def it_computes_right_edge(self):
        assert Rectangle(x=10, y=0, width=50, height=20).right == 60

    def it_computes_bottom_edge(self):
        assert Rectangle(x=0, y=10, width=50, height=20).bottom == 30


class WhenTranslatingDraw:
    def it_places_bitmap_at_the_correct_canvas_position(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=10, offset_y=20)
        icon = Image.new("1", (16, 16), 0)

        translated.bitmap((5, 5), icon, fill=(0, 0, 0))

        mock_draw.bitmap.assert_called_once_with((15, 25), icon, fill=(0, 0, 0))

    def it_places_text_at_the_correct_canvas_position(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=5, offset_y=10)

        translated.text((0, 0), "hello", fill=(0, 0, 0))

        mock_draw.text.assert_called_once_with((5, 10), "hello", fill=(0, 0, 0))

    def it_places_rectangle_at_the_correct_canvas_position(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=10, offset_y=20)

        translated.rectangle([0, 0, 50, 30], outline="black")

        mock_draw.rectangle.assert_called_once_with([10, 20, 60, 50], outline="black")

    def it_places_ellipse_at_the_correct_canvas_position(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=10, offset_y=20)

        translated.ellipse([0, 0, 30, 30], fill="yellow")

        mock_draw.ellipse.assert_called_once_with([10, 20, 40, 50], fill="yellow")

    def it_places_points_at_the_correct_canvas_positions(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=10, offset_y=20)

        translated.point([5, 10, 15, 20])

        mock_draw.point.assert_called_once_with([15, 30, 25, 40])

    def it_draws_nothing_when_point_list_is_empty(self):
        mock_draw = MagicMock()
        translated = TranslatedDraw(mock_draw, offset_x=10, offset_y=20)

        translated.point([])

        mock_draw.point.assert_called_once_with([])
