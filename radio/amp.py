from gpiozero import OutputDevice, Device
import utils as utils
from constants import AMP_RELAY

amp_relay = OutputDevice(AMP_RELAY, active_high=False, initial_value=False)

logger = utils.create_logger(__name__)
STATE = utils.state()

def off():
    # speaker disconnect
    logger.debug('amp off')
    amp_relay.off()


def on():
    # speaker connect
    logger.debug('amp on')
    amp_relay.on()
off()
