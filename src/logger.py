import logging

import config

DEFAULT_LOG_SEVERITY = logging.DEBUG
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logger = logging.getLogger('main')
logger.setLevel(DEFAULT_LOG_SEVERITY)

log_stream = logging.StreamHandler()
log_stream.setLevel(DEFAULT_LOG_SEVERITY)

log_formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

log_stream.setFormatter(log_formatter)

logger.addHandler(log_stream)
