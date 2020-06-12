import requests
import xmltodict
import datetime
import time

import constants as CONST

coordinates = {
    "lat": str(CONST.LAT),
    "lon": str(CONST.LONG),
    "msl": str(CONST.ELEV),
}

def parse_datetime(dt_str):
    """Parse datetime."""
    return time.mktime(datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z").timetuple())

def get_weather():
    r = requests.get('https://api.met.no/weatherapi/locationforecast/1.9/', params=coordinates)
    data = xmltodict.parse(r.text)["weatherdata"]

    c = 0
    prec_sum = 0
    threshold = False

    for entry in data["product"]["time"]:
        time_diff = int(parse_datetime(entry["@to"]) - parse_datetime(entry["@from"]))
        if time_diff == 3600:
            prec = float(entry['location']['precipitation']['@value'])
            if prec > CONST.PREC_THRESHOLD:
                threshold = True
            prec_sum += prec

        c += 1
        if c >= 80:
            break

    if threshold or prec_sum > CONST.PREC_SUM_THRESHOLD:
        return True
    else:
        return False

get_weather()
