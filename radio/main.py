import mpv
import json
import threading
import time

# Load stations file
with open('stations.json') as stations_file:
  stations = json.load(stations_file)

current_station = ''
player = ''

def play_stream(stream_name):
    global current_station
    global player
    current_station = stream_name
    player = mpv.MPV()
    player.play(stations[stream_name]['url'])
    player.wait_for_playback()

player_thread = threading.Thread(target=play_stream, args=('fritz',))
player_thread.start()
while not hasattr(player, "metadata"):
    time.sleep(1)
while not "icy-title" in player.metadata:
    time.sleep(1)

last_tag = ''
while True:
    tag = player.metadata['icy-title']

    if last_tag != player.metadata['icy-title'] and player.metadata['icy-title'] not in stations[current_station]['skip_strings']:
        for replace_string in stations[current_station]['replace_strings']:
            tag = tag.replace(replace_string, '').lstrip()
        print(tag)
        last_tag = player.metadata['icy-title']
    time.sleep(1)