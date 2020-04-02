import mpv
import json
import threading
import time

# # Load stations file
# with open('stations.json') as stations_file:
#   stations = json.load(stations_file)
player = mpv.MPV()
player.playlist_append('http://rbb-fritz-live.cast.addradio.de/rbb/fritz/live/mp3/128/stream.mp3')
player.playlist_append('http://st01.dlf.de/dlf/01/128/mp3/stream.mp3')
# player.playlist_next()


while True:
    # To modify the playlist, use player.playlist_{append,clear,move,remove}. player.playlist is read-only
    print(player.playlist)
    player.wait_for_playback()




# def play_stream(stream_name):
#     global current_station
#     global player
#     player = mpv.MPV()
#     player.wait_for_playback()

# player_thread = threading.Thread(target=play_stream, args=('fritz',))