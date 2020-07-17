import threading
from time import sleep, time

from pirc522 import RFID


from enums import PlaybackMode
import constants as CONST
import utils
import radio

logger = utils.create_logger('rfid')
STATE = utils.state()

# Load stations and music library file
stations, music_lib = utils.openFiles()

rdr = RFID()


# thread start stop
rfid_thread = None


def _rfid_loop():
    t = threading.current_thread()
    last_stop = 0

    while t.name is 'run':
        sleep(1)

        last_time_tag_detected = False

        rdr.wait_for_tag()
        (error, tag_type) = rdr.request()
        if not error:
            (error, uid) = rdr.anticoll()
            # logger.debug("Tag with UID: {} detected".format(uid))
            if not error:
                rfid = str(utils.uid_to_num(uid))
                last_time_tag_detected = True

                if STATE['playback_mode'] is not PlaybackMode.CD:
                    # TODO: disconnect all bt devices

                    diff = time() - last_stop  # time since tag was removed

                    if 60 < diff:  # restart cd playback
                        radio.start_cd(
                            CONST.MUSIC_LIB_PATH + music_lib[rfid])
                        logger.debug(
                            "CD Player started fresh with playlist: {}".format(radio.get_player().playlist))
                    else:
                        radio.start_cd(None)
                        logger.debug(
                            "CD Player resumed with old playlist: {}".format(radio.get_player().playlist))

        # else:
        #     print("error in rdr request")
        #     # resume radio?

        if STATE['playback_mode'] is PlaybackMode.CD:
            # tag was removed
            if last_time_tag_detected is False:
                radio.pause_cd()
                last_stop = time()

                # switch back to radio
                STATE['playback_mode'] = PlaybackMode.Radio
                radio.unmute_unpause_current_player()


def start_thread():
    global rfid_thread

    if rfid_thread is not None:
        return

    rfid_thread = threading.Thread(target=_rfid_loop)
    rfid_thread.name = 'run'
    rfid_thread.start()


def stop_thread():
    global rfid_thread

    if rfid_thread is None:
        return

    rfid_thread.name = 'stop'
    rfid_thread = None
