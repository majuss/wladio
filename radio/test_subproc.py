
import threading
import mpv
from time import sleep as t_sleep
import sys


def write_flushed(str):
    sys.stdout.write(str)
    sys.stdout.write('\n')
    sys.stdout.flush()


radioPlayer = mpv.MPV(
    demuxer_max_back_bytes=100 * 1000 * 1000,
    demuxer_max_bytes=10*1000*1000,
    demuxer_donate_buffer='no',
    loop_file='inf')
#    log_handler=mpv_debug_logger)
# radioPlayer.set_loglevel('trace')

radioPlayer.volume = 20
radioPlayer.pause = True
radioPlayer.command('stop')

# radioPlayer.playlist_append(
#     'https://st01.sslstream.dlf.de/dlf/01/high/aac/stream.aac')
# radioPlayer.playlist_append(
#     'https://www.antennebrandenburg.de/live.m3u')

radioPlayer.playlist_pos = 0
radioPlayer.pause = False
radioPlayer.mute = False

commands = {}


def register_command(command, function):
    commands[command] = function


def next(args):
    playlist_items = len(radioPlayer.playlist)

    playlist_position = radioPlayer.playlist_pos
    playlist_position += 1

    if playlist_position is playlist_items:
        playlist_position = 0

    radioPlayer.playlist_pos = playlist_position

    write_flushed('log: next')


def prev(args):
    playlist_position = radioPlayer.playlist_pos
    playlist_position -= 1

    if playlist_position == -1:
        playlist_position = len(radioPlayer.playlist) - 1

    radioPlayer.playlist_pos = playlist_position

    write_flushed('log: prev')


def add_playlist(args):
    radioPlayer.playlist_append(args)
    write_flushed('log: added ' + args)


def unmute(args):
    radioPlayer.pause = False


def unpause(args):
    radioPlayer.mute = False


def set_playlist_pos(args):
    radioPlayer.playlist_pos = int(args)


def set_volume(args):
    radioPlayer.volume = int(args)


register_command('next', next)
register_command('prev', prev)
register_command('add playlist', add_playlist)
register_command('unmute', unmute)
register_command('unpause', unpause)
register_command('set playlist pos', set_playlist_pos)
register_command('set volume', set_volume)


def read_commands():
    while True:
        command = sys.stdin.readline()[:-1]

        doublepoint_pos = command.find(':')
        command_name = command[0:doublepoint_pos]
        command_args = command[doublepoint_pos+1:]

        if not (command_name in commands):
            write_flushed('not supported command: ' + command_name)
            continue

        write_flushed('command is: "' + command_name + '"')
        write_flushed('args is: "' + command_args + '"')

        try:
            commands[command_name](command_args)
        except:
            write_flushed('log: failed to execute "' +
                          command_name + '" with "' + command_args + '"')


tag_thread = threading.Thread(target=read_commands)
tag_thread.start()
