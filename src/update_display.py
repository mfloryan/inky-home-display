#!/usr/bin/env python3

import argparse
import logging
import os
from datetime import datetime

from display import display
from data.house_sensors import get_house_temperatures
from data.public_transport import get_morning_departures_cached
from data.thermia import get_outdoor_temp
from data.tibber import tibber_energy_prices, tibber_energy_stats
from data.weather import get_weather

def collect_data():
    current_time = datetime.now()
    return {
        "current_time": current_time,
        "energy_prices": tibber_energy_prices(),
        "energy_stats": tibber_energy_stats(),
        "weather": get_weather(),
        "transport": get_morning_departures_cached(current_time),
        "heatpump_outdoor_temp": get_outdoor_temp(),
        "house_temps": get_house_temperatures(),
    }


def main():
    parser = argparse.ArgumentParser(description="Update Inky home display")
    parser.add_argument(
        "--png-only",
        action="store_true",
        help="Force PNG output, do not try to use Inky hardware",
    )
    parser.add_argument(
        "--output", default="out/test.png", help="PNG output file path (default: out/test.png)"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if not os.getenv("DEBUG"):
        logging.getLogger("pymodbus").setLevel(logging.WARNING)

    display(collect_data(), prefer_inky=not args.png_only, png_output_path=args.output)


if __name__ == "__main__":
    main()
