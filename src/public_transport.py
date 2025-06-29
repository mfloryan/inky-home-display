import requests
import os

# SideId -  9680: Näsbypark (Täby)
#           2254: Runskriftsrondellen


def getDeparturesBasedOnTimeOfDay():
    departures = {}
    departures["Stockholm"] = getDeparturesToStockholm()
    return departures


def getDeparturesToStockholm():
    return


def getDepaturesToNasbyPark():
    return


def getDeparturesForSiteId(siteid):
    api_key = os.environ.get("SL_API_KEY")

    if not api_key:
        raise RuntimeError("SL_API_KEY environment variable not defined")

    sl_response = requests.get(
        "https://api.sl.se/api2/realtimedeparturesV4.json",
        {"key": api_key, "siteid": siteid, "timewindow": 30},
    )

    sl_data = sl_response.json()

    def mapBusses(busDeparture):
        return {
            "number": busDeparture["LineNumber"],
            "dest": busDeparture["Destination"],
            "dir": busDeparture["JourneyDirection"],
            "depature_time": busDeparture["TimeTabledDateTime"],
        }

    return {
        "age_in_seconds": sl_data["ResponseData"]["DataAge"],
        "busses": list(map(mapBusses, sl_data["ResponseData"]["Buses"])),
    }
