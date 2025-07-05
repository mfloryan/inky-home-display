import datetime
from unittest.mock import MagicMock

from display import Rectangle, HeaderWidget
from display_backend import PngFileBackend


class TestHeaderWidget:
    def test_header_widget_renders_polish_date_at_widget_origin(self):

        bounds = Rectangle(4, 0, 396, 25)
        current_time = datetime.datetime(2023, 12, 25, 14, 30)
        widget = HeaderWidget(bounds, current_time)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args

        # Widget should draw at its own origin (0,0)
        assert call_args[0][0] == (0, 0)
        # Should use black color
        assert call_args[1]["fill"] == colours[0]
        # Should render Polish date format for Monday, December 25, 2023
        text_content = call_args[0][1]
        assert "poniedziałek 25 grudnia 2023" == text_content.lower()
