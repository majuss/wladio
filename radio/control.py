import RPi.GPIO as GPIO
import subprocess
from time import sleep


import display
import radio
import speakers
import bluetooth
import power
import rfid
import utils
import constants as CONST
from enums import PlaybackMode, PowerState


logger = utils.create_logger(__name__)
STATE = utils.state()

GPIO.setmode(GPIO.BCM)

GPIO.setup(CONST.GARAGE_RELAY, GPIO.OUT)
GPIO.output(CONST.GARAGE_RELAY, GPIO.HIGH)

GPIO.setup(CONST.DRIVEWAY_RELAY, GPIO.OUT)
GPIO.output(CONST.DRIVEWAY_RELAY, GPIO.HIGH)


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


def control_real_prev():
    logger.debug('control_real_prev')
    radio.real_prev()

    if STATE['playback_mode'] is PlaybackMode.Radio:
        display.main_text(radio.get_stream_name())


def control_next():
    logger.debug('control_next')
    radio.next()

    if STATE['playback_mode'] is PlaybackMode.Radio:
        display.main_text(radio.get_stream_name())


def control_skip_forward():
    logger.debug('control_skip_forward')
    radio.skip_forward()


def control_skip_backward():
    logger.debug('control_skip_backward')
    radio.skip_backward()


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
    bluetooth.stop_thread()

    speakers.off()

    try:
        display.enter_standby()
        subprocess.call(["rfkill", "block", "bluetooth"])
    except Exception as e:
        logger.warning('Set power state failed {}'.format(e))


def control_leave_standby():
    logger.debug('control_leave_standby')

    sleep(CONST.RELAIS_DELAY)
    speakers.on()

    radio.leave_standby()

    display.leave_standby()
    subprocess.call(["rfkill", "unblock", "bluetooth"])

    bluetooth.start_thread()


def control_toggle_shuffle_cd():
    radio.toggle_shuffle_cd()

    if STATE['power_state'] is PowerState.Powered:
        display.hard_refresh_top_viewport()


def control_bluetooth_device_connected():
    logger.debug('control_bluetooth_device_connected')

    rfid.stop_thread()
    radio.mute_radio_and_pause_cd()
    STATE['playback_mode'] = PlaybackMode.BT
    STATE['draw_bluetooth_icon'] = True
    display.hard_refresh_top_viewport()
    display.main_text('Bluetoothmodus')


def control_bluetooth_device_disconnected():
    logger.debug('control_bluetooth_device_disconnected')

    STATE['playback_mode'] = PlaybackMode.Radio
    radio.unmute_unpause_current_player()
    STATE['draw_bluetooth_icon'] = False

    if STATE['power_state'] is PowerState.Powered:
        display.hard_refresh_top_viewport()
        rfid.start_thread()


def control_drivewaygate():
    logger.debug('control_drivewaygate')

    power.stop_thread()

    if STATE['power_state'] is PowerState.Standby:
        display.leave_standby()

    display.forced_text('Einfahrt auf/zu', CONST.DOORS_TIMEOUT)
    GPIO.output(CONST.DRIVEWAY_RELAY, GPIO.LOW)
    sleep(0.5)
    GPIO.output(CONST.DRIVEWAY_RELAY, GPIO.HIGH)

    if STATE['power_state'] is PowerState.Standby:
        sleep(CONST.DOORS_TIMEOUT)
        display.enter_standby()

    power.start_thread()


def control_garagedoor():
    logger.debug('control_garagedoor')

    power.stop_thread()

    if STATE['power_state'] is PowerState.Standby:
        display.leave_standby()

    display.forced_text('Garagentor auf/zu', CONST.DOORS_TIMEOUT)
    GPIO.output(CONST.GARAGE_RELAY, GPIO.LOW)
    sleep(0.5)
    GPIO.output(CONST.GARAGE_RELAY, GPIO.HIGH)

    if STATE['power_state'] is PowerState.Standby:
        sleep(CONST.DOORS_TIMEOUT)
        display.enter_standby()

    power.start_thread()


def control_save_trace():
    display.forced_text('SAVE TRACE', 10)
    radio.save_mpv_trace()
