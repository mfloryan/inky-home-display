#!/usr/bin/env python3

from display import display
from tibber import tibber_energy_prices
from weather import get_weather

#from test_fonts import test_fonts
#from public_transport import getDeparturesBasedOnTimeOfDay, getDeparturesForSiteId


def main():
    data = {'energy_prices': tibber_energy_prices(), 'weather': get_weather()}
    # transport = getDeparturesBasedOnTimeOfDay()
    # print(transport)
    display(data)


main()
