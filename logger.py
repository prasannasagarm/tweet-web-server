import logging
import logging.handlers

LOG_FILE='logs/log_project_place.out'

log = logging.getLogger('pplogger')
log.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(LOG_FILE,
						maxBytes=10*1024,
						backupCount=5)

log.addHandler(handler)
