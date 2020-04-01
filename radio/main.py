import mpv
import json

# Load stations file
with open('stations.json') as stations_file:
  stations = json.load(stations_file)

current_station = ''


def stream_logger(loglevel, component, message):
    global current_station
    if message.lstrip() not in stations[current_station]['skip_strings'] and "icy-title" in message:
        for replace_string in stations[current_station]['replace_strings']:
            message = message.replace(replace_string, "")
        print(message.lstrip())

def play_stream(streamObj, logger):
    player = mpv.MPV(log_handler=logger)
    player.play(streamObj['url'])
    player.wait_for_playback()

    return streamObj['key']

current_station = play_stream(stations['fritz'], stream_logger)
