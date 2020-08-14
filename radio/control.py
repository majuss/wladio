import subprocess
from time import sleep


import display
import radio
import speakers
import utils
from enums import PlaybackMode


logger = utils.create_logger(__name__)
STATE = utils.state()


def control_up(diff):
    logger.debug('control_up')
    player = radio.get_player()
    if player is None:
        return
    radio.up(diff)
    display.overlay_rect(int(256 / 100 * player.volume), 1)


def control_down(diff):
    logger.debug('control_down')
    player = radio.get_player()
    if player is None:
        return
    radio.down(diff)
    display.overlay_rect(int(256 / 100 * player.volume), 1)


def control_prev():
    logger.debug('control_prev')
    radio.prev()

    if STATE['playback_mode'] is PlaybackMode.Radio:
        display.main_text(radio.get_stream_name())


def control_next():
    logger.debug('control_next')
    radio.next()

    # im after file track change no metadata is available
    if STATE['playback_mode'] is PlaybackMode.Radio:
        display.main_text(radio.get_stream_name())


def control_pause_toggle():
    logger.debug('control_pause_toggle')

    player = radio.get_player()
    if player is None:
        return

    radio.pause_toggle()

    if STATE['paused']:
        display.set_pause_or_mute_text('Pause')

    else:
        display.remove_pause_or_mute_text()


def control_mute_toggle():
    logger.debug('control_mute_toggle')

    player = radio.get_player()
    if player is None:
        return

    radio.mute_toggle()

    if STATE['muted']:
        display.set_pause_or_mute_text('Lautlos')

    else:
        display.remove_pause_or_mute_text()


def control_enter_standby():
    logger.debug('control_enter_standby')
    radio.enter_standby()
    utils.save_radio_conf()

    speakers.off()

    try:
        display.set_standby_onoff(True)
        subprocess.call(["rfkill", "block", "bluetooth"])
    except Exception as e:
        logger.warning('Set power state failed {}'.format(e))


def control_leave_standby():
    logger.debug('control_leave_standby')

    sleep(CONST.RELAIS_DELAY)
    speakers.on()

    radio.leave_standby()

    display.set_standby_onoff(False)
    subprocess.call(["rfkill", "unblock", "bluetooth"])
