import mpv
import time

import utils as utils
import constants as CONST

from enums import *


logger = utils.create_logger(__name__)
STATE = utils.state()


# Load stations and music library file
radioStations, music_lib = utils.openFiles()


radioPlayer = mpv.MPV()
radioPlayer.volume = STATE['radio_volume']
radioPlayer.pause = True
radioPlayer.command('stop')


cdPlayer = mpv.MPV(loop_playlist='inf')
cdPlayer.volume = CONST.CD_PLAYER_START_VOL
toggle_cd = False


# add stream urls to radio playlist
for station in radioStations:
    radioPlayer.playlist_append(radioStations[station]['url'])


# handels

def next():
    logger.debug('next')

    player = get_player()
    if player is None:
        return

    num_playlists = len(player.playlist)

    if STATE['radio_playlist_position'] + 1 is num_playlists:
        player.playlist_pos = 0
    else:
        player.playlist_next()

    STATE['radio_playlist_position'] = player.playlist_pos


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

    if 2 < diff_time and diff_time < 10:  # only when two button presses occure in a time frame from greater 2 and smaller 10 seconds
        player.seek(-15)
    elif diff_time < 2:
        if STATE['radio_playlist_position'] - 1 is -1:
            player.playlist_pos = len(player.playlist) - 1
        else:
            player.playlist_prev()

        STATE['radio_playlist_position'] = player.playlist_pos


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

    global toggle_cd

    if toggle_cd:
        cdPlayer.command('playlist-unshuffle')
    else:
        cdPlayer.command('playlist-shuffle')

    toggle_cd = not toggle_cd


def unmute_unpause_current_player():
    logger.debug('unmute_unpause_current_player')

    player = get_player()
    if player is None:
        return

    STATE['muted'] = STATE['paused'] = player.mute = player.pause = False
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

    elif STATE['playback_mode'] is PlaybackMode.CD:
        cdPlayer.mute = cdPlayer.pause = False

    STATE['paused'] = STATE['muted'] = False


#############################
# return current active player acording to state
def get_player():
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
        except:
            pass
            logger.error('Couldnt get CD tag')

    return 'No title found'


def _get_current_station_name():
    url = radioPlayer.playlist[radioPlayer.playlist_pos]['filename']
    for station in radioStations:
        if url == radioStations[station]['url']:
            return radioStations[station]['name']
    logger.debug('no station name found for ' + str(url))
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

        if CONST.RADIO_MAX_PAUSE_DIFF < diff:
            radioPlayer.playlist_pos = STATE['radio_playlist_position']
            print(diff)
