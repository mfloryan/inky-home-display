import datetime
from unittest.mock import MagicMock

from display_backend import PngFileBackend
from widgets import FooterWidget, HeaderWidget, Rectangle


class TestHeaderWidget:
    def test_header_widget_renders_polish_date_at_widget_origin(self):
        bounds = Rectangle(4, 0, 396, 25)
        current_time = datetime.datetime(2023, 12, 25, 14, 30)
        mock_font_loader = MagicMock()
        widget = HeaderWidget(bounds, mock_font_loader, current_time)

        mock_draw = MagicMock()
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args

        assert call_args[0][0] == (0, 0)
        assert call_args[1]["fill"] == colours[0]
        text_content = call_args[0][1]
        assert "poniedziałek 25 grudnia 2023" == text_content.lower()


class TestFooterWidget:
    def test_footer_widget_renders_update_timestamp_at_bottom_right(self):
        bounds = Rectangle(200, 287, 200, 13)
        current_time = datetime.datetime(2023, 12, 25, 14, 30, 45)
        mock_font_loader = MagicMock()
        mock_font_loader.terminus_regular_12.return_value = "mock_font"
        widget = FooterWidget(bounds, mock_font_loader, current_time)

        mock_draw = MagicMock()
        mock_draw.textbbox.return_value = (0, 0, 150, 12)
        backend = PngFileBackend()
        colours = backend.colors

        widget.render(mock_draw, colours)

        mock_draw.text.assert_called_once()
        call_args = mock_draw.text.call_args

        assert call_args[0][0] == (50, 1)
        assert call_args[0][1] == "Updated: Mon 25 Dec 2023 14:30:45 "
        assert call_args[1]["fill"] == colours[1]
