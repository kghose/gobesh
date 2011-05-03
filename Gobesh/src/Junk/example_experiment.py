"""An example of an experiment written using the Gobesh framework. This 
experiment runs a two interval forced choice experiment"""

import logging
import logging.handlers
import sys
sys.path.append('Modules/')
import gobesh #For logger

    
if len(sys.argv) > 1:
    level_name = sys.argv[1]
else:
  level_name = 'debug'

logger = gobesh.setup_logger(fname='gobesh.log', level_name=level_name)


state = 'BEGIN'
data = {'instruction': 'nothing'}

logger.info('Starting main loop')
while state != 'END':
  """Keep looping until the state machine says 'END' at which point we quit
  the server with the apropriate shutdown routines."""
  poll_all_devices(data) #Poll all devices and update our data structure
  
  if state == 'BEGIN':
    if data['instruction'] == 'Trial Start':
      state = 'NEW TRIAL'
  elif state == 'NEW TRIAL':
    #Initialize new trial
    if data['instruction'] == 'Stop':
      
  
  
  


logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical error message')
