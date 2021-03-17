import logging
from uvicorn.logging import DefaultFormatter

from app import config

ch = logging.StreamHandler()
log_format = '%(asctime)s - %(levelprefix)s %(name)s: %(message)s'
formatter = DefaultFormatter(fmt=log_format)
ch.setFormatter(formatter)

logging.basicConfig(
	level=config.LOG_LEVEL,
	#format='%(asctime)s - %(levelprefix)s %(name)s: %(message)s',
	handlers=[ch]
)
logging.getLogger('prethink').setLevel(logging.WARNING)


def get_logger(name=__name__, level='DEBUG'):
	logger = logging.getLogger(name)

	return logger
