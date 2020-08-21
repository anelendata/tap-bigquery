import logging, sys


LOGGER = None


def get_logger(name="handoff"):
    global LOGGER
    if not LOGGER:
        logging.basicConfig(
            stream=sys.stdout,
            format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
            level=logging.INFO)
        LOGGER = logging.getLogger(name)
    return LOGGER
