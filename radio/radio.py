import mpv
import time


import utils as utils
import constants as CONST

from enums import *


logger = utils.create_logger('radio')

STATE = utils.state()


# Load stations and music library file
radioStations, music_lib = utils.openFiles()


radioPlayer = mpv.MPV()
radioPlayer.volume = CONST.RADIO_PLAYER_START_VOL
radioPlayer.pause = True
radioPlayer.command('stop')


cdPlayer = mpv.MPV()

# add stream urls to radio playlist
for station in radioStations:
    radioPlayer.playlist_append(radioStations[station]['url'])


def check_start():
    logger.debug('check_start')

    if STATE['power_state'] is PowerState.Powered:  # radio is powerd
        radioPlayer.playlist_pos = STATE['radio_playlist_position']
        radioPlayer.pause = False

        STATE['paused'] = False

        logger.debug('radio playback started')


# handels

def next():
    logger.debug('next')

    player = get_player()
    if player == None:
        return

    num_playlists = len(player.playlist)

    if STATE['radio_playlist_position'] + 1 == num_playlists:
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
    if player == None:
        return

    diff_time = time.time() - last_prev
    last_prev = time.time()

    if 2 < diff_time and diff_time < 10:  # only when two button presses occure in a time frame from greater 2 and smaller 10 seconds
        player.seek(-15)
    elif diff_time < 2:
        if STATE['radio_playlist_position'] - 1 == -1:
            player.playlist_pos = len(player.playlist) - 1
        else:
            player.playlist_prev()

        # TODO: uncoment / display
        # if playback_mode == PlaybackMode.Radio:
        #    display.main_text(get_current_station_name(radioPlayer, stations))

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


def enter_standby():
    logger.debug('enter_standby')

    if STATE['playback_mode'] is PlaybackMode.Radio:
        logger.debug('stop radio player')
        radioPlayer.command('stop', 'keep-playlist')

    elif STATE['playback_mode'] is PlaybackMode.CD:
        logger.debug('pause cd player')
        cdPlayer.pause = True

    STATE['paused'] = True


def leaf_standby():
    logger.debug('leaf_standby')

    if STATE['playback_mode'] is PlaybackMode.Radio:
        radioPlayer.playlist_pos = STATE['radio_playlist_position']
        radioPlayer.mute = False

    elif STATE['playback_mode'] is PlaybackMode.CD:
        cdPlayer.mute = cdPlayer.pause = False

    STATE['paused'] = STATE['muted'] = False


#############################
# return current active player acording to state
def get_player():
    if STATE['playback_mode'] == PlaybackMode.Radio:
        return radioPlayer
    if STATE['playback_mode'] == PlaybackMode.CD:
        return cdPlayer
    return None


def get_stream_name():
    player = get_player()
    if player == None:
        return 'NO TITLE'

    if STATE['playback_mode'] == PlaybackMode.Radio:
        return _get_current_station_name()

    if STATE['playback_mode'] == PlaybackMode.CD:
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
    if player == None:
        return

    new_vol = player.volume + amount

    if new_vol < 0:
        new_vol = 0
    elif new_vol > 100: # restrict to 100 .volume can go up to 999 until it throws exception
        new_vol = 100

    player.volume = new_vol

