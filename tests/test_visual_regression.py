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
                # 00:00-05:45 - Night: low prices (0.8-1.2 SEK) - hours 0-5, quarters 0-23
                0.95, 0.93, 0.90, 0.88, 0.88, 0.86, 0.84, 0.82, 0.82, 0.84, 0.86, 0.89,
                0.89, 0.91, 0.92, 0.94, 0.94, 0.93, 0.92, 0.91, 0.91, 0.92, 0.93, 0.94,
                # 06:00-11:45 - Morning peak around 8am (1.8-3.7 SEK) - hours 6-11, quarters 24-47
                1.20, 1.45, 1.65, 1.85, 2.15, 2.45, 2.70, 2.95, 3.15, 3.40, 3.55, 3.65,
                3.65, 3.50, 3.35, 3.21, 3.05, 2.95, 2.90, 2.85, 2.75, 2.65, 2.55, 2.45,
                # 12:00-17:45 - Day: moderate (1.7-2.2 SEK) - hours 12-17, quarters 48-71
                2.35, 2.25, 2.20, 2.15, 2.10, 2.05, 2.00, 1.95, 1.85, 1.80, 1.78, 1.75,
                1.75, 1.78, 1.82, 1.85, 1.90, 1.95, 2.00, 2.05, 2.05, 2.00, 1.98, 1.95,
                # 18:00-23:45 - Evening peak around 6pm (2.8-4.0 SEK) - hours 18-23, quarters 72-95
                2.25, 2.55, 2.70, 2.85, 3.05, 3.25, 3.35, 3.45, 3.65, 3.80, 3.88, 3.95,
                3.95, 3.88, 3.82, 3.75, 3.55, 3.40, 3.32, 3.25, 3.15, 3.05, 2.95, 2.85
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
            "current_time": datetime(2024, 1, 15, 10, 30, 0),  # Monday 10:30 AM
            "transport": [
                {
                    "stop_name": "Roslags Näsby",
                    "destination": "Stockholms östra",
                    "line_number": "27",
                    "scheduled_time": datetime(2024, 1, 15, 10, 38, 0),
                    "transport_mode": "TRAM",
                    "journey_state": "NORMALPROGRESS",
                    "walk_time_minutes": 10,
                    "is_missed": False,
                },
                {
                    "stop_name": "Lahällsviadukten",
                    "destination": "Danderyds sjukhus",
                    "line_number": "605",
                    "scheduled_time": datetime(2024, 1, 15, 10, 42, 0),
                    "transport_mode": "BUS",
                    "journey_state": "EXPECTED",
                    "walk_time_minutes": 6,
                    "is_missed": False,
                },
                {
                    "stop_name": "Roslags Näsby",
                    "destination": "Stockholms östra",
                    "line_number": "27",
                    "scheduled_time": datetime(2024, 1, 15, 10, 53, 0),
                    "transport_mode": "TRAM",
                    "journey_state": "EXPECTED",
                    "walk_time_minutes": 10,
                    "is_missed": False,
                },
            ]
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
