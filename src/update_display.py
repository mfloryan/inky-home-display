#!/usr/bin/env python3

from display import display
from tibber import tibber_energy_prices
from weather import get_weather

#from test_fonts import test_fonts
#from public_transport import getDeparturesBasedOnTimeOfDay, getDeparturesForSiteId


def main():
    data = {}
    data['energy_prices'] = tibber_energy_prices()
    # transport = getDeparturesBasedOnTimeOfDay()
    # print(transport)
    data['weather'] = get_weather()
    display(data)


main()
