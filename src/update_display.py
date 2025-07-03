#!/usr/bin/env python3

import argparse
from datetime import datetime
from display import display
from tibber import tibber_energy_prices, tibber_energy_stats
from weather import get_weather
# from test_fonts import test_fonts
# from public_transport import getDeparturesBasedOnTimeOfDay, getDeparturesForSiteId


def main():
    parser = argparse.ArgumentParser(description='Update Inky home display')
    parser.add_argument('--png-only', action='store_true',
                        help='Force PNG output, do not try to use Inky hardware')
    parser.add_argument('--output', default='img/test.png',
                        help='PNG output file path (default: img/test.png)')

    args = parser.parse_args()

    data = {
        "energy_prices": tibber_energy_prices(),
        "energy_stats": tibber_energy_stats(),
        "weather": get_weather(),
        "current_time": datetime.now(),
    }
    # transport = getDeparturesBasedOnTimeOfDay()
    # print(transport)

    prefer_inky = not args.png_only
    display(data, prefer_inky=prefer_inky, png_output_path=args.output)


if __name__ == "__main__":
    main()
