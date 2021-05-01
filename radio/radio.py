import gc
import signal
import mpv
import time
import tracemalloc

import utils as utils
import constants as CONST

# from enums import *
from enums import PlaybackMode


logger = utils.create_logger(__name__)
STATE = utils.state()


# Load stations and music library file
radioStations, music_lib = utils.openFiles()


mpv_msgs = []


def mpv_debug_logger(level, prefix, text):
    now = time.time()
    while len(mpv_msgs):
        mpv_msg = mpv_msgs[0]

        diff = now - mpv_msg['t']

        if 60 * 5 < diff:
            mpv_msgs.pop(0)
        else:
            break

    mpv_msgs.append({'t': time.time(), 'm': str(level) +
                     ' ' + str(prefix) + ' ' + str(text)})


radioPlayer = mpv.MPV(
    demuxer_max_back_bytes=100 * 1000 * 1000,
    demuxer_max_bytes=10*1000*1000,
    demuxer_donate_buffer='no',
    loop_file='inf')
#    log_handler=mpv_debug_logger)
# radioPlayer.set_loglevel('trace')

radioPlayer.volume = STATE['radio_volume']
radioPlayer.pause = True
radioPlayer.command('stop')


# debugging start


# def radio_callback(event):
#     print(event)
# radioPlayer.register_event_callback(radio_callback)


# @radioPlayer.event_callback('end-file')
# def my_handler(event):
#     logger.debug('radioPlayer event end-file:')
#     print(event)


# gc.set_debug( gc.DEBUG_STATS) # | gc.DEBUG_LEAK)
gc.enable()


def handler(signum, frame):
    logger.debug('SIGUSR1 debug info radioPlayer')

    logger.debug('collected trace msgs: ' + str(len(mpv_msgs)))

    logger.debug(
        'volume pause mute core_idle idle_active demuxer_cache_duration demuxer_cache_time')
    logger.debug(str(radioPlayer.volume))
    logger.debug(str(radioPlayer.pause))
    logger.debug(str(radioPlayer.mute))
    logger.debug(str(radioPlayer.core_idle))
    logger.debug(str(radioPlayer.idle_active))
    logger.debug(str(radioPlayer.demuxer_cache_duration))
    logger.debug(str(radioPlayer.demuxer_cache_time))

    gc.collect()
    logger.debug('gc.garbage length: ' + str(len(gc.garbage)))
    logger.debug('gc enabled: ' + str(gc.isenabled()))
    logger.debug('gc counts: ' + str(gc.get_count()))

    logger.debug('UNCOLLECTABLE objects start')

    for obj in gc.garbage:
        try:
            logger.debug(str(obj))
        except Exception as e:
            logger.debug('Error in gc.garbage loop: {}'.format(e))
            pass

    logger.debug('UNCOLLECTABLE objects end')


# Set the signal handler and a 5-second alarm
# signal.signal(signal.SIGUSR1, handler)

first_snapshot = None


# def inital_snapshot(signum, frame):
#     global first_snapshot

#     gc.collect()
#     first_snapshot = tracemalloc.take_snapshot()
# signal.signal(signal.SIGUSR1, inital_snapshot)

# def run_tracemalloc(signum, frame):

#     gc.collect()
#     snapshot = tracemalloc.take_snapshot()
#     # top_stats = snapshot.statistics('filename', True)

#     # for stat in top_stats:
#     #     print(stat)
#     # for line in stat.traceback.format():
#     #     print(line)
#     # print('###############################################################################')


#     print('####################################')
#     print('difference')

#     top_stats = snapshot.compare_to(first_snapshot, 'filename', True)

#     unchanged = 0
#     for stat in top_stats:
#         if stat.count_diff == 0:
#             print(stat)
#         else:
#             unchanged += 1
#     print('unchanged blocks ' + str(unchanged))


# signal.signal(signal.SIGUSR2, run_tracemalloc)


# debugging end


cdPlayer = mpv.MPV(loop_playlist='inf')
cdPlayer.volume = CONST.CD_PLAYER_START_VOL


# add stream urls to radio playlist
for station in radioStations:
    radioPlayer.playlist_append(station['url'])
logger.debug('number of playlists loaded: ' + str(len(radioPlayer.playlist)))

last_trace_save = 0
# dump_mpv_trace


def save_mpv_trace():
    logger.debug('save mpv trace')
    global last_trace_save
    global radioPlayer

    diff = time.time() - last_trace_save

    if diff < 60:
        logger.debug('saved less than a minute ago')
        return

    last_trace_save = time.time()

    # Open a file with access mode 'a'
    with open('/home/pi/mpv_trace_at_' + str(time.time()) + '.txt', 'a') as file_object:
        for mpv_obj in mpv_msgs:
            file_object.write(str(mpv_obj['t']) + ' ' + mpv_obj['m'] + '\n')
        file_object.close()

    radioPlayer.pause = not radioPlayer.pause

    time.sleep(1)

    radioPlayer.pause = not radioPlayer.pause


def next():
    logger.debug('next')

    player = get_player()
    if player is None:
        return

    playlist_items = len(player.playlist)

    if STATE['playback_mode'] is PlaybackMode.Radio:
        playlist_position = STATE['radio_playlist_position']
        playlist_position += 1

        if playlist_position is playlist_items:
            playlist_position = 0

        player.playlist_pos = playlist_position

        STATE['radio_playlist_position'] = playlist_position

    if STATE['playback_mode'] is PlaybackMode.CD:
        if player.playlist_pos + 1 is playlist_items:
            player.playlist_pos = 0
        else:
            player.playlist_next()


def real_prev():
    logger.debug('real_prev')

    player = get_player()
    if player is None:
        return

    if STATE['playback_mode'] is PlaybackMode.Radio:
        playlist_position = STATE['radio_playlist_position']
        playlist_position -= 1

        if playlist_position is -1:
            playlist_position = len(player.playlist) - 1

        player.playlist_pos = playlist_position

        STATE['radio_playlist_position'] = playlist_position

    if STATE['playback_mode'] is PlaybackMode.CD:
        if player.playlist_pos - 1 == -1:
            player.playlist_pos = len(player.playlist) - 1
        else:
            player.playlist_prev()


# when was prev last pressed?
last_prev = 0


def prev():
    logger.debug('prev')
    global last_prev

    player = get_player()
    if player is None:
        return

    diff_time = time.time() - last_prev
    last_prev = time.time()

    if 2 < diff_time and diff_time < 10:  # only when two button presses occure in a \
        # time frame from greater 2 and smaller 10 seconds
        player.seek(-15)
    elif diff_time < 2:
        real_prev()


def skip_forward():
    logger.debug('skip_forward')

    player = get_player()
    if player is None:
        return

    player.seek(10)


def skip_backward():
    logger.debug('skip_backward')

    player = get_player()
    if player is None:
        return

    player.seek(-10)


def up(diff):
    logger.debug('up')
    _volume_change(diff)


def down(diff):
    logger.debug('down')
    _volume_change(diff)


def pause_toggle():
    logger.debug('pause toggle')

    player = get_player()
    if player is None:
        return

    STATE['paused'] = player.pause = not player.pause

    _check_radio_pause()

    if player.pause is False:  # unmute if unpaused
        STATE['muted'] = player.mute = False


def mute_toggle():
    logger.debug('mute_toggle')

    player = get_player()
    if player is None:
        return

    STATE['muted'] = player.mute = not player.mute

    if player.mute is False:  # unpause if unmuted
        STATE['paused'] = player.pause = False
        _check_radio_pause()


def mute_radio_and_pause_cd():
    cdPlayer.pause = True
    radioPlayer.mute = True

    STATE['muted'] = STATE['paused'] = True


def mute_radio():
    radioPlayer.mute = True


def pause_cd():
    cdPlayer.pause = True


def start_cd(path):
    radioPlayer.mute = True

    STATE['playback_mode'] = PlaybackMode.CD

    if path is not None:
        cdPlayer.play(path)

    STATE['paused'] = STATE['muted'] = cdPlayer.pause = cdPlayer.mute = False


def toggle_shuffle_cd():
    if STATE['playback_mode'] is not PlaybackMode.CD:
        return

    if STATE['shuffle_cd']:
        cdPlayer.command('playlist-unshuffle')
    else:
        cdPlayer.command('playlist-shuffle')

    STATE['shuffle_cd'] = not STATE['shuffle_cd']


def unmute_unpause_current_player():
    logger.debug('unmute_unpause_current_player')

    logger.debug('get_player() for state {}'.format(STATE['playback_mode']))

    player = get_player()
    if player is None:
        return

    STATE['muted'] = STATE['paused'] = player.mute = player.pause = False
    logger.debug('_check_radio_pause()')
    _check_radio_pause()


def enter_standby():
    logger.debug('enter_standby')

    if STATE['playback_mode'] is PlaybackMode.Radio:
        logger.debug('stop radio player')
        radioPlayer.command('stop', 'keep-playlist')

    elif STATE['playback_mode'] is PlaybackMode.CD:
        logger.debug('pause cd player')
        cdPlayer.pause = True

    STATE['paused'] = True


def leave_standby():
    logger.debug('leave_standby')

    if STATE['playback_mode'] is PlaybackMode.Radio:
        radioPlayer.playlist_pos = STATE['radio_playlist_position']
        radioPlayer.mute = radioPlayer.pause = False

        logger.debug('unmute unpause, play station ' +
                     str(radioPlayer.playlist_pos))

    elif STATE['playback_mode'] is PlaybackMode.CD:
        cdPlayer.mute = cdPlayer.pause = False

    STATE['paused'] = STATE['muted'] = False


def get_player():
    """return current active player acording to state"""

    if STATE['playback_mode'] is PlaybackMode.Radio:
        return radioPlayer
    if STATE['playback_mode'] is PlaybackMode.CD:
        return cdPlayer
    return None


def get_stream_name():
    player = get_player()
    if player is None:
        return 'NO TITLE'

    if STATE['playback_mode'] is PlaybackMode.Radio:
        return _get_current_station_name()

    if STATE['playback_mode'] is PlaybackMode.CD:
        try:
            player = get_player()

            txt = '(' + str(player.playlist_pos + 1) + \
                '/' + str(player.playlist_count) + ')'

            txts = []
            if 'title' in player.metadata:
                txts.append(player.metadata['title'])
            if 'artist' in player.metadata:
                txts.append(player.metadata['artist'])

            txts = txt + ' ' + ' - '.join(txts)

            return txts
        except Exception as e:
            pass
            logger.error('Couldnt get CD tag: {}'.format(e))

    return 'No title found'


def _get_current_station_name():
    try:
        return radioStations[radioPlayer.playlist_pos]['name']
    except Exception as e:
        pass
        logger.debug('no station name found for position: {} {}'.format(
            str(radioPlayer.playlist_pos), e))
        return 'NO STATION FOUND'


# change player volume
def _volume_change(amount):
    logger.debug('change volume ' + str(amount))

    player = get_player()
    if player is None:
        return

    new_vol = player.volume + amount

    if new_vol < 0:
        new_vol = 0
    elif new_vol > 100:  # restrict to 100 .volume can go up to 999 until it throws exception
        new_vol = 100

    logger.debug('new volume ' + str(new_vol))

    player.volume = new_vol

    if STATE['playback_mode'] is PlaybackMode.Radio:
        STATE['radio_volume'] = new_vol


def _check_radio_pause():
    if STATE['playback_mode'] is not PlaybackMode.Radio:
        return

    if STATE['paused']:
        STATE['radio_last_pause'] = time.time()

    if STATE['paused'] is False or STATE['muted'] is False:
        diff = time.time() - STATE['radio_last_pause']

        if CONST.RADIO_MAX_PAUSE_DIFF < diff:  # reset radio playback to live
            radioPlayer.playlist_pos = STATE['radio_playlist_position']
            # print(diff)
