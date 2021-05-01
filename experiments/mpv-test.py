
import threading
from time import sleep
import mpv

radioPlayer = mpv.MPV(
    demuxer_max_back_bytes=100 * 1000 * 1000,
    demuxer_max_bytes=10*1000*1000,
    demuxer_donate_buffer='no',
    loop_file='inf')
#    log_handler=mpv_debug_logger)
# radioPlayer.set_loglevel('trace')

radioPlayer.volume = 50
radioPlayer.pause = True
radioPlayer.command('stop')

radioPlayer.playlist_append(
    'https://st01.sslstream.dlf.de/dlf/01/high/aac/stream.aac')
radioPlayer.playlist_append(
    'https://www.antennebrandenburg.de/live.m3u')
radioPlayer.playlist_pos = 0
radioPlayer.pause = False
radioPlayer.mute = False


radioPlayer.playlist_next()


def print_tags():
    while True:
        sleep(1)
        print('test')


tag_thread = threading.Thread(target=print_tags)
tag_thread.start()
