import logging
import logging.handlers

import sys
sys.path.append('../Modules/')

import modu1

LOG_FILENAME = 'gobesh.log'
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
else:
  level = logging.NOTSET

logging.basicConfig(filename=LOG_FILENAME, 
                    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=level)  

logger = logging.getLogger('Gobesh')

modu1.run()
print 'Ha'

logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical error message')
