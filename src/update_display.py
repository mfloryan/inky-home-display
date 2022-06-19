#!/usr/bin/env python3

from display import display

#from test_fonts import test_fonts
from public_transport import getDeparturesBasedOnTimeOfDay, getDeparturesForSiteId

def main():
    
    data = {}
    data['energy_prices'] = [
        0.0823, 0.0741, 0.0663, 0.0625, 0.0602, 0.0631, 0.0675, 0.0773, 0.0894, 0.1086,
        0.1205, 0.1328, 0.1336, 0.1312, 0.1429, 0.2184, 0.4004, 0.4677, 1.0719, 1.0126,
        0.5912, 0.6686, 0.4447, 0.3952
    ]
    # transport = getDeparturesBasedOnTimeOfDay()
    # print(transport)
    display(data)

main()
