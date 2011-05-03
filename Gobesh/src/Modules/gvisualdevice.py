"""An example device that uses pyglet and pylab to generate visual stimuli.
This illustrates how to write devices that have a server component. The
program that shows the visual stimuli runs as a server. This module, when 
imported as a device into gobesh, gives a 'hook' that allows the experiment
server (Gobesh) to interact with the stimulus server.
"""

import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

class GVisualDevice:
  """The device that can be instantiated by the Gobesh server to talk to the
  visual stimulus server, that is started separately."""
  def __init__(self):
    #The interface for the class
    #Can be accessed by calling .interface
    self.interface = {}
      
  def initialize(self, vars):
    """This is called when the server initializes. Use this to setup the screen
    etc."""
    self.address = vars.get('address','')
    self.port = vars.get('port',6001)
    self.authkey = vars.get('authkey','gobesh visual demo device')
        
    self.parent_conn, child_conn = mp.Pipe()
    self.p = mp.Process(target=self.deviceloop, args=(child_conn,))
    self.p.start()
  
  def quit(self):
    """This is called when the server is about to quit."""
    self.parent_conn.send('quit') #The thread (deviceloop) must understand this
    self.p.join() #or we will hang
    
  def poll(self, timestamp, state_event, input_vars):
    """This is the call that is visible to the main loop. The main loop calls
    this each time it loops. state_event and variables are picked out to be the
    state_event and global variables that are connected to this device
    The return value should be the event that the
    device's loop returns. In the case of the controller device we don't care
    about state_events, timestamps or variables."""
    device_event = None
    output_variables = None
    if self.parent_conn.poll():
      #We have a message
      msg = self.parent_conn.recv()
      if msg[0] == 'device event':
        device_event = msg[1]
      else:
        device_event = None
        
    return device_event, output_variables

  def deviceloop(self, child_conn):
    """This is the function that runs in the other thread. 
    Child conn is the communication line to the other thread."""
    keep_running = True
    #Do initialization here
    #address = ('localhost', 6001)     # family is deduced to be 'AF_INET'
    listener = mp.connection.Listener((self.address, self.port), authkey='gobesh demo')

    remote_conn = listener.accept()
    logger.debug('connection accepted from:' + listener.last_accepted[0] + ':%d' %(listener.last_accepted[1]))
    
    while keep_running:
      if remote_conn.poll():
        c = remote_conn.recv()
        if c == '1':
          child_conn.send(['device event','1'])
        if c == '2':
          child_conn.send(['device event','2'])
        if c == '3':
          child_conn.send(['data request'])
#      r = random.randint(0,50)
#      if r == 0:
#        child_conn.send(['device event','1'])
#      if r == 50:
#        child_conn.send(['device event','2'])
#      if r == 25:
#        child_conn.send(['data request'])
      
      if child_conn.poll():
        msg = child_conn.recv()
        if msg[0] == 'command':
          if msg[1] == 'quit':
            logger.debug('Demo device recieved quit signal')
            keep_running = False
        if msg[0] == 'data':
          a = msg[1][0]
          b = msg[1][1]
          x = a - b
          y = a + b
          child_conn.send(['data',[x,y]])
      time.sleep(0.01)

    remote_conn.close()
    child_conn.close()
