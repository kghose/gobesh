"""This module provides the basic controller device. It also provides a simple
text based front end for testing."""

import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

#Imports for this device
import time #For the sleep function

class GController:
  """Though this is written as just another device, note that a given experiment
  has just one controller."""
  def __init__(self):
    #The interface for the class
    #Can be accessed by calling .interface
    self.interface = \
    {'input variables': {},
     'input events': {},
     'output events': {'go': 'Start the experiment by moving it from the wait phase',
                       'abort': 'Halt the experiment by moving to the wait phase',
                       'quit': 'Quit our server'}}
      
  def initialize(self, variables):
    """This is called when the server initializes."""
    self.parent_conn, child_conn = mp.Pipe()
    self.p = mp.Process(target=self.deviceloop, args=(child_conn,))
    self.p.start()
  
  def quit(self):
    """This is called when the server is about to quit."""
    self.parent_conn.send('quit') #The thread (deviceloop) must understand this
    self.p.join() #or we will hang
    
  def poll(self, timestamp, state_event, variables):
    """This is the call that is visible to the main loop. The main loop calls
    this each time it loops. state_event and variables are picked out to be the
    state_event and global variables that are connected to this device
    The return value should be the event that the
    device's loop returns. In the case of the controller device we don't care
    about state_events, timestamps or variables."""
    device_event = None
    if self.parent_conn.poll():
      #We have a message
      msg = self.parent_conn.recv()
      if msg[0] == 'device event':
        device_event = msg[1]
      else:
        device_event = None
        
    return device_event
  
  def deviceloop(self, child_conn):
    """Child conn is the communication line to the other thread."""
    keep_running = True
    #Do initialization here
    address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
    listener = mp.connection.Listener(address, authkey='gobesh controller')

    remote_conn = listener.accept()
    logger.debug('connection accepted from:' + listener.last_accepted[0] + ':%d' %(listener.last_accepted[1]))
    
    while keep_running:
      if child_conn.poll():
        msg = child_conn.recv()
        print msg
        if msg == 'quit':
          keep_running = False
 
      if remote_conn.poll():
        msg = remote_conn.recv()
        child_conn.send(['device event', msg])

      time.sleep(0.01)
    remote_conn.send('Bye') #Tells controller we can quit