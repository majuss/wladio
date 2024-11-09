import subprocess
from time import sleep

import display
import radio
import speakers
import amp
import bluetooth
import power
import rfid
import utils
import constants as CONST
from enums import PlaybackMode, PowerState

logger = utils.create_logger(__name__)
STATE = utils.state()

# Define relays using gpiozero
# driveway_relay = OutputDevice(CONST.DRIVEWAY_RELAY, active_high=False, initial_value=False)

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

def control_leave_standby():
    logger.debug('control_leave_standby')

    amp.on()
    sleep(2)
    speakers.on()

    radio.leave_standby()
    display.leave_standby()
    subprocess.call(["rfkill", "unblock", "bluetooth"])
    bluetooth.start_thread()

def control_enter_standby():
    logger.debug('control_enter_standby')

    speakers.off()
    sleep(CONST.RELAIS_DELAY)
    amp.off()

    radio.enter_standby()
    utils.save_radio_conf()
    bluetooth.stop_thread()

    try:
        display.enter_standby()
        subprocess.call(["rfkill", "block", "bluetooth"])
    except Exception as e:
        logger.warning('Set power state failed {}'.format(e))

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
        # rfid.start_thread()

def control_drivewaygate():
    logger.debug('control_drivewaygate')
    # return
    import requests

    # Home Assistant URL and API token
    HA_URL = "http://0.0.0.0:8123"
    API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhNDA5MzcwZGJmM2U0ZjE0YmI4NGMyNDlmODQwN2E3ZCIsImlhdCI6MTcyODkzMTg1NywiZXhwIjoyMDQ0MjkxODU3fQ.lH_CW3W4WBf-CpK7RQCHBJ397nb9yF0YzgKVhdH1etI"

    # The entity ID of the switch you want to toggle
    entity_id = "switch.einfahrt_kanal_b"

    # API endpoint for toggling a switch
    url = f"{HA_URL}/api/services/switch/toggle"

    # Headers, including Authorization using the API token
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    # Data payload: The entity_id of the switch to toggle
    data = {
        "entity_id": entity_id
    }

    # Make the POST request to toggle the switch
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Switch toggled successfully!")
    else:
        print(f"Failed to toggle switch. Status code: {response.status_code}")
        print(response.text)


    # power.stop_thread()
    # if STATE['power_state'] is PowerState.Standby:
    #     display.leave_standby()
    # display.forced_text('Einfahrt auf/zu', CONST.DOORS_TIMEOUT)
    # driveway_relay.on() #
    # sleep(1)
    # driveway_relay.off()
    # if STATE['power_state'] is PowerState.Standby:
    #     sleep(CONST.DOORS_TIMEOUT)
    #     display.enter_standby()
    # power.start_thread()

def control_garagedoor():
    logger.debug('control_garagedoor')
    import requests

    # Home Assistant URL and API token
    HA_URL = "http://0.0.0.0:8123"
    API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhNDA5MzcwZGJmM2U0ZjE0YmI4NGMyNDlmODQwN2E3ZCIsImlhdCI6MTcyODkzMTg1NywiZXhwIjoyMDQ0MjkxODU3fQ.lH_CW3W4WBf-CpK7RQCHBJ397nb9yF0YzgKVhdH1etI"

    # The entity ID of the switch you want to toggle
    entity_id = "switch.garagentor_taster"

    # API endpoint for toggling a switch
    url = f"{HA_URL}/api/services/switch/toggle"

    # Headers, including Authorization using the API token
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    # Data payload: The entity_id of the switch to toggle
    data = {
        "entity_id": entity_id
    }

    # Make the POST request to toggle the switch
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Switch toggled successfully!")
    else:
        print(f"Failed to toggle switch. Status code: {response.status_code}")
        print(response.text)
    # return
    # power.stop_thread()
    # if STATE['power_state'] is PowerState.Standby:
    #     display.leave_standby()
    # display.forced_text('Garagentor auf/zu', CONST.DOORS_TIMEOUT)
    # amp_relay.on()
    # sleep(0.5)
    # amp_relay.off()
    # if STATE['power_state'] is PowerState.Standby:
    #     sleep(CONST.DOORS_TIMEOUT)
    #     display.enter_standby()
    # power.start_thread()

def control_save_trace():
    display.forced_text('SAVE TRACE', 10)
    radio.save_mpv_trace()
