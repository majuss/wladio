#!/usr/bin/env python3
import mpv

player = mpv.MPV(ytdl=True, input_default_bindings=True, input_vo_keyboard=True)

player.playlist_append('https://youtu.be/PHIGke6Yzh8')
player.playlist_append('https://youtu.be/Ji9qSuQapFY')
player.playlist_append('https://youtu.be/6f78_Tf4Tdk')

player.playlist_pos = 0

while True:
    # To modify the playlist, use player.playlist_{append,clear,move,remove}. player.playlist is read-only
    print(player.playlist)
    player.wait_for_playback()
