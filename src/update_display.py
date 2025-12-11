#!/usr/bin/env python3

import argparse
import logging
from datetime import datetime

from display import display
from public_transport import get_morning_departures_cached
from tibber import tibber_energy_prices, tibber_energy_stats
from weather import get_weather

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Update Inky home display')
    parser.add_argument('--png-only', action='store_true',
                        help='Force PNG output, do not try to use Inky hardware')
    parser.add_argument('--output', default='out/test.png',
                        help='PNG output file path (default: out/test.png)')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    current_time = datetime.now()

    energy_prices = None
    try:
        energy_prices = tibber_energy_prices()
    except Exception as e:
        logger.error("Failed to fetch Tibber energy prices: %s", e)

    energy_stats = None
    try:
        energy_stats = tibber_energy_stats()
    except Exception as e:
        logger.error("Failed to fetch Tibber energy stats: %s", e)

    data = {
        "energy_prices": energy_prices,
        "energy_stats": energy_stats,
        "weather": get_weather(),
        "transport": get_morning_departures_cached(current_time),
        "current_time": current_time,
    }

    prefer_inky = not args.png_only
    display(data, prefer_inky=prefer_inky, png_output_path=args.output)


if __name__ == "__main__":
    main()
