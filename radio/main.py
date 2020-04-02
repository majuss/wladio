import mpv
import json
import threading
import time
import sys

# Load stations file
with open('stations.json') as stations_file:
  stations = json.load(stations_file)

current_station = ''
player = mpv.MPV()

for station in stations:
    player.playlist_append(stations[station]['url'])

def play_stream():
    # while getattr(player_thread, "signal", True):
    player.wait_for_playback()

def next_stream():
    player.playlist_pos = 2
    player.wait_for_playback()

print(player.playlist)
player_thread = threading.Thread(target=play_stream)
player_thread.start()
player_thread.daemon = True
print(threading.enumerate())
time.sleep(10)

player_thread.join()
player2_thread = threading.Thread(target=next_stream)

# player.playlist_next()

player2_thread.start()
print(threading.enumerate())
print(player.playlist)

# while not hasattr(player, "metadata"):
#     time.sleep(1)
# while not "icy-title" in player.metadata:
#     time.sleep(1)

# last_tag = ''
# while True:
#     tag = player.metadata['icy-title']

#     if last_tag != player.metadata['icy-title'] and player.metadata['icy-title'] not in stations[current_station]['skip_strings']:
#         for replace_string in stations[current_station]['replace_strings']:
#             tag = tag.replace(replace_string, '').lstrip()
#         print(tag)
#         last_tag = player.metadata['icy-title']
#     time.sleep(1)