import mpv
import time
import threading

def play_stream():
    while True:
        player.wait_for_property('core-idle', lambda x: not x)
        player.wait_for_property('core-idle')

player = mpv.MPV()
player.wait_for_property('idle-active')

player.playlist_append('http://rbb-fritz-live.cast.addradio.de/rbb/fritz/live/mp3/128/stream.mp3')
player.playlist_append('http://st01.dlf.de/dlf/01/128/mp3/stream.mp3')

player.playlist_pos = 0
player_thread = threading.Thread(target=play_stream)
player_thread.start()

time.sleep(5)
player.playlist_pos = 1
time.sleep(5)
player.playlist_pos = 0
print(player.playlist[player.playlist_pos])

# player.pause = False
# player.wait_for_playback()

#!/usr/bin/env python3
# import time
# import os
# import sys
# import threading

# import mpv
# player = mpv.MPV()

# # def runner():
# #     while True:
# #         player.wait_for_property('core-idle') # wait for pause
# #         print('core-idle')
# #         time.sleep(1)

# # t = threading.Thread(target=runner)

# player.play('http://rbb-fritz-live.cast.addradio.de/rbb/fritz/live/mp3/128/stream.mp3')

# player.wait_for_property('core-idle', lambda x: not x) # wait for stream to load
# # t.start()

# paused = False
# while True:
#     input()
#     paused = not paused
#     player.pause = paused
#     print('paused', paused)

# sys.exit(0)