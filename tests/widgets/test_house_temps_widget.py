from unittest.mock import MagicMock

from display_backend import PngFileBackend
from widgets import HouseTempReading, HouseTempsViewData, HouseTempsWidget, Rectangle


def _make_widget(readings):
    bounds = Rectangle(0, 0, 120, 79)
    font_loader = MagicMock()
    return HouseTempsWidget(bounds, font_loader, HouseTempsViewData(readings=readings))


class WhenRenderingHouseTempsWidget:
    def it_renders_the_dom_header_in_yellow(self):
        widget = _make_widget([HouseTempReading(label="Salon", temp=22.2)])
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 20
        colours = PngFileBackend().colors

        widget.render(mock_draw, colours)

        text_calls = {call[0][1]: call[1]["fill"] for call in mock_draw.text.call_args_list}
        assert "DOM" in text_calls
        assert text_calls["DOM"] == colours[1]

    def it_renders_a_label_and_temperature_for_each_reading(self):
        widget = _make_widget([
            HouseTempReading(label="Salon", temp=22.2),
            HouseTempReading(label="Sypialnia", temp=20.1),
            HouseTempReading(label="Kuchnia", temp=22.8),
        ])
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 20

        widget.render(mock_draw, PngFileBackend().colors)

        text_content = [call[0][1] for call in mock_draw.text.call_args_list]
        assert "Salon" in text_content
        assert "Sypialnia" in text_content
        assert "Kuchnia" in text_content
        assert "22.2°C" in text_content
        assert "20.1°C" in text_content
        assert "22.8°C" in text_content

    def it_positions_each_reading_below_the_previous_one(self):
        widget = _make_widget([
            HouseTempReading(label="Salon", temp=22.2),
            HouseTempReading(label="Sypialnia", temp=20.1),
        ])
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 20

        widget.render(mock_draw, PngFileBackend().colors)

        label_ys = [
            call[0][0][1]
            for call in mock_draw.text.call_args_list
            if call[0][1] in ("Salon", "Sypialnia")
        ]
        assert label_ys[1] > label_ys[0]

    def it_renders_with_a_single_reading(self):
        widget = _make_widget([HouseTempReading(label="Salon", temp=22.2)])
        mock_draw = MagicMock()
        mock_draw.textlength.return_value = 20

        widget.render(mock_draw, PngFileBackend().colors)

        text_content = [call[0][1] for call in mock_draw.text.call_args_list]
        assert "DOM" in text_content
        assert "Salon" in text_content
        assert "22.2°C" in text_content
