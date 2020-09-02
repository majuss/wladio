import threading
from time import sleep, time

from pirc522 import RFID


from enums import PlaybackMode
import constants as CONST
import utils
import radio
import display

logger = utils.create_logger(__name__)
STATE = utils.state()

cd_paths_without_id = utils.get_cd_paths_without_id()

# Load stations and music library file
stations, music_lib = utils.openFiles()

rdr = RFID()


# thread start stop
rfid_thread = None


def _rfid_loop():
    t = threading.current_thread()
    last_stop = 0
    max_cont_fails = 0

    SET_CD_LIB = CONST.SET_CD_LIB
    write_cd_lib_mode = False
    last_set_cd = None
    last_played_rfid_tag = ""

    while t.name == 'run':
        sleep(2 / CONST.MAX_CONT_FAILS)

        rdr.wait_for_tag(0.5)
        (error, tag_type) = rdr.request()
        if not error:
            (error, uid) = rdr.anticoll()
            if not error:
                # logger.debug("Tag with UID: {} detected".format(uid))
                max_cont_fails = 0
                rfid = str(utils.uid_to_num(uid))

                if SET_CD_LIB == rfid and write_cd_lib_mode is False:
                    write_cd_lib_mode = True
                    display.forced_text('Karte weg (3 sec)', 5)
                    sleep(4)
                elif SET_CD_LIB == rfid and write_cd_lib_mode is True:
                    write_cd_lib_mode = False
                    last_set_cd = None
                    display.forced_text('Karte weg (3 sec)', 5)
                    sleep(4)
                    continue

                cd_path = None
                
                if write_cd_lib_mode:
                    if last_set_cd is not None: # write tag
                        """try to assign new cd, fall through for next selection """
                        if rfid in music_lib:
                            display.forced_text('CD existiert', 5)
                            continue

                        display.forced_text('CD gespeichert', 5)
                        logger.debug('assign: "' + rfid + '" to CD: ' + cd_paths_without_id[0])
                        music_lib[rfid] = cd_paths_without_id[0]
                        utils.save_music_lib()
                        last_set_cd = None
                        cd_paths_without_id.pop(0)
                        sleep(5)

                    if last_set_cd is None:
                        if 0 == len(cd_paths_without_id):
                            display.forced_text('no cds to sort', 5)
                            continue

                        cd_path = CONST.MUSIC_LIB_PATH + cd_paths_without_id[0]
                        last_set_cd = cd_paths_without_id[0]
                        display.forced_text('place cd card', 5)
                        STATE['playback_mode'] = PlaybackMode.Unknown


                elif write_cd_lib_mode is False:
                    if rfid not in music_lib:
                        continue

                    cd_path = CONST.MUSIC_LIB_PATH + music_lib[rfid]

                    if rfid != last_played_rfid_tag: # tag changed
                        last_stop = 0
                        STATE['playback_mode'] = PlaybackMode.Unknown


                if STATE['playback_mode'] is not PlaybackMode.CD and STATE['playback_mode'] is not PlaybackMode.BT:
                    last_played_rfid_tag = rfid
                    # TODO: disconnect all bt devices

                    diff = time() - last_stop  # time since tag was removed

                    if 60 < diff:  # restart cd playback
                        radio.start_cd(cd_path)
                        logger.debug(
                            "CD Player started fresh with playlist: {}".format(radio.get_player().playlist))
                    else:
                        radio.start_cd(None)
                        logger.debug(
                            "CD Player resumed with old playlist: {}".format(radio.get_player().playlist))
                continue
            logger.debug('error rdr.anticoll()')

        max_cont_fails += 1

        if write_cd_lib_mode is True or max_cont_fails < CONST.MAX_CONT_FAILS:
            logger.debug('error rdr.request(), fails ' + str(max_cont_fails))
            continue

        if STATE['playback_mode'] is PlaybackMode.CD:
            # tag was removed
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
