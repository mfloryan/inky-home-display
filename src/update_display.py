#!/usr/bin/env python3

from display import display
from tibber import todays_prices

#from test_fonts import test_fonts
from public_transport import getDeparturesBasedOnTimeOfDay, getDeparturesForSiteId

def main():
    
    data = {}
    data['energy_prices'] = todays_prices()
    # transport = getDeparturesBasedOnTimeOfDay()
    # print(transport)
    display(data)

main()
