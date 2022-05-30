# Create a logger object.
import logging
import coloredlogs

import emoji

logger = logging.getLogger('file_module')
coloredlogs.install(level='DEBUG')

# Some examples.
logger.debug("this is a debugging message")
logger.info("this is an informational message")
logger.warning("this is a warning message")
logger.error("this is an error message")
logger.critical("this is a critical message")


