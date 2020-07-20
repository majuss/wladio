import threading
import requests
import xmltodict
import datetime
import time
import sys

import constants as CONST
import utils


logger = utils.create_logger(__name__)
STATE = utils.state()

coordinates = {
    "lat": str(CONST.LAT),
    "lon": str(CONST.LONG),
    "msl": str(CONST.ELEV),
}


def parse_datetime(dt_str):
    """Parse datetime."""
    return time.mktime(datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z").timetuple())


def get_weather():
    """Calls metno API for weather forecast and returns True/False depending on precipitation"""
    r = requests.get(
        'https://api.met.no/weatherapi/locationforecast/1.9/', params=coordinates)
    data = xmltodict.parse(r.text)["weatherdata"]

    c = 0
    prec_sum = 0
    threshold = False

    for entry in data["product"]["time"]:
        time_diff = int(parse_datetime(
            entry["@to"]) - parse_datetime(entry["@from"]))
        if time_diff is 3600:
            prec = float(entry['location']['precipitation']['@value'])
            if prec > CONST.PREC_THRESHOLD:
                threshold = True
            prec_sum += prec

        c += 1
        if c >= 80:
            break
    logger.debug("Precipitation sum: {}".format(prec_sum))
    if threshold or prec_sum > CONST.PREC_SUM_THRESHOLD:
        return True
    else:
        return False


# thread start stop
weather_thread = None


def _weather_loop():
    t = threading.current_thread()
    while t.name is 'run':
        rain = get_weather()
        rain = True
        STATE['draw_rain_cloud_icon'] = rain
        logger.debug('Weather set to {}'.format(rain))
        time.sleep(60)


def start_thread():
    global weather_thread

    if weather_thread is not None:
        return

    weather_thread = threading.Thread(target=_weather_loop)
    weather_thread.name = 'run'
    weather_thread.start()


def stop_thread():
    global weather_thread

    if weather_thread is None:
        return

    weather_thread.name = 'stop'
    weather_thread = None
