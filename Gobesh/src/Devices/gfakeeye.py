"""An device that pretends to be generating eye position data."""

import basedevice
logger = logging.getLogger('Gobesh.'+__name__)

class GFakeEye(basedevice.GBaseDevice):
  """A general controller device we can use in our experiments. Note that at
  high data rates, like 1 kHz, this may not keep up, depending on your operating 
  system."""

  def setup_interface(self):
    self.interface = \
    {'device type': 'Eye position simulator',
     'description': 'Pretends to be an eye position device like a video tracker',
     'input variables': [['target','Target x,y as tuple', 'f', False, False, (0,0)],#Note that we have data type as 'f', it is really a tuple or list and we can't handle this in the interface yet but we don't need to  
                         ['motivation', 'Value from 0 to 1 indicating how strongly the eye will saccade to that location, instead of saccading to a random location', 'f', False, False, 0.5]
                         ['rate','rate (Hz) of data production', 'f', True, True, 200]],
     'output variables': [['position','Current eye position as x,y pair']],
     'input events': [['start', 'Start producing data', True],
                      ['stop', 'Stop producing data', True]],
     'output events': []}

  def deviceloop(self):
    """."""
    logger.debug('Starting device loop')    
    keep_running = True
    producing_data = False
    T_sample = 1/.self.rate
    last_sample_generated_ms = 0
    while keep_running:
      if not self.queue_from_parent.empty()
        msg = self.queue_from_parent.get()
        if msg[0] == 'event':
          #Code to handle events
          event_name = msg[1]
          if event_name == 'quit':
            keep_running = False
          elif event_name == 'start':
            if not producing_data:
              producing_data = True
              data_sample
          elif event_name == 'stop':
            producing_data = False
      if producing_data:
        
      
    logger.debug('Exited controller')
        