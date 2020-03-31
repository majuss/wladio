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

def play_stream(stream_name):
    global current_station
    current_station = stream_name
    player = mpv.MPV(log_handler=stream_logger)
    player.play(stations[stream_name]['url'])
    player.wait_for_playback()

play_stream('fritz')