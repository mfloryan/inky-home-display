from datetime import datetime
import pytest
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from display import display


class TestVisualRegression:
    @pytest.mark.manual
    @pytest.mark.mpl_image_compare
    def test_display_generates_image_with_winter_data(self):
        # Realistic Swedish winter energy data
        test_data = {
            "energy_prices": [
                # Night: low prices (0.8-1.2 SEK)
                0.95, 0.88, 0.82, 0.89, 0.94, 0.91,
                # Morning peak around 8am (2.5-3.8 SEK)
                1.85, 2.95, 3.65, 3.21, 2.85, 2.45,
                # Day: moderate (1.5-2.5 SEK)
                2.15, 1.95, 1.75, 1.85, 2.05, 1.95,
                # Evening peak around 6pm (3.0-4.0 SEK)
                2.85, 3.45, 3.95, 3.75, 3.25, 2.85
            ],
            "energy_stats": {
                "production": 0.0,  # No solar in Swedish winter
                "consumption": 15.3,
                "profit": 0.0,
                "cost": 45.67
            },
            "weather": {
                "name": "Stockholm",
                "sunrise": datetime(2024, 1, 15, 8, 47),
                "sunset": datetime(2024, 1, 15, 15, 12),
                "now": {"temp": -8.5},
                "forecast": [
                    {"time": datetime(2024, 1, 15, 12, 0), "temp": -6, "weather": "pochmurnie"},
                    {"time": datetime(2024, 1, 15, 15, 0), "temp": -9, "weather": "śnieg"},
                    {"time": datetime(2024, 1, 15, 18, 0), "temp": -12, "weather": "bezchmurnie"},
                    {"time": datetime(2024, 1, 15, 21, 0), "temp": -15, "weather": "mroźnie"}
                ]
            },
            "current_time": datetime(2024, 1, 15, 10, 30, 0)  # Monday 10:30 AM
        }

        test_output_path = "out/winter_display_test.png"

        # Generate test image
        display(test_data, prefer_inky=False, png_output_path=test_output_path)

        img = mpimg.imread(test_output_path)

        height, width, _ = img.shape
        output_dpi = 100
        fig_width_inches = width / output_dpi
        fig_height_inches = height / output_dpi

        fig, ax = plt.subplots(figsize=(fig_width_inches, fig_height_inches), dpi=output_dpi)

        ax.imshow(img, interpolation='nearest', resample=False)
        ax.set_axis_off()
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove all margins

        return fig
