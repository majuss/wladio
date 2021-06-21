import threading
import requests
import datetime
import time
import json

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
    }
    r = requests.get(
        "https://api.met.no/weatherapi/locationforecast/2.0?lat={}&lon={}".format(
            CONST.LAT, CONST.LONG
        ),
        headers=headers,
    )

    data = json.loads(r.text)

    prec_sum = 0
    threshold = False
    prec_sum = (
        data["properties"]["timeseries"][0]["data"]["next_6_hours"]["details"][
            "precipitation_amount"
        ]
        + data["properties"]["timeseries"][9]["data"]["next_6_hours"]["details"][
            "precipitation_amount"
        ]
    )
    if prec_sum > CONST.PREC_THRESHOLD:
        threshold = True
    logger.debug("Precipitation sum: {}".format(prec_sum))
    if threshold or prec_sum > CONST.PREC_SUM_THRESHOLD:
        return True
    else:
        return False


# thread start stop
weather_thread = None


def _weather_loop():
    t = threading.current_thread()
    while t.name == 'run':
        rain = get_weather()
        # rain = True # comment to use real data
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
