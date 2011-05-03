"""This module provides the basic controller device. It also provides a simple
text based front end for testing."""

import basedevice

class GController(basedevice.GBaseDevice):
  """A general controller device we can use in our experiments"""

  def setup_interface(self):
    self.interface = \
    {'device type': 'Standard Controller',
     'description': 'Standard controller that responds to user input to start, abort, stop and quit experiments',
     'input variables': [],
     'output variables': [],
     'input events': [['start', 'Start the experiment', True],
                      ['abort', 'Stop running immediately', True],
                      ['stop', 'Stop running after we have finished some stuff', True],
                      ['quit', 'Quit all devices and exit', True]],
     'output events': [['start', 'Start the experiment'],
                       ['abort', 'Stop running immediately'],
                       ['stop', 'Stop running after we have finished some stuff'],
                       ['quit', 'Quit all devices and exit']]}

  def deviceloop(self):
    """This really does nothing except wait until we have a quit signal."""
    logger.debug('Starting device loop')
    keep_running = True
    while keep_running:
      msg = self.queue_from_parent.get()
      if msg[0] == 'event':
        #Code to handle events
        event_name = msg[1]
        if event_name == 'quit':
          keep_running = False
            
    logger.debug('Exited controller')