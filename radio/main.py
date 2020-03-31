import mpv
import json

with open('stations.json') as stations_file:
  stations = json.load(stations_file)

def stream_logger(loglevel, component, message):
    if message.lstrip() not in stations['fritz']['skip_strings'] and "icy-title" in message:
        for replace_string in stations['fritz']['replace_strings']:
            message = message.replace(replace_string, "")
        print(message.lstrip())
#replace Jetzt läuft

player = mpv.MPV(log_handler=stream_logger)
player.play(stations['fritz']['url'])
player.wait_for_playback()
