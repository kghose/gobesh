"""This module provides an example device that illustrates the API that has to
be exposed to Gobesh."""

import multiprocessing as mp #For threading
import logging #We should make use of the logging function
logger = logging.getLogger('Gobesh.'+__name__)

class GDemoDevice0:
  """This demo device illustrates the barebones of writing a device that
  Gobesh can instantiate and run."""
  def __init__(self):
    """Use this to do any fixed initialization. This is called when the server
    (main loop) instantiates the device objects"""
    pass
      
  def initialize(self, config_dir = './', my_name = 'ADemoDevice'):
    """This is called when the main loop initializes. Gobesh will pass it
    It loads settings from
    the settings file, creates pipes to communicate with the child process and
    then starts the child process."""
    self.generate_config_fname(config_dir, my_name)
    self.load_settings()

    #Fixed code that should be same for all devices that start a child thread
    self.parent_conn, child_conn = mp.Pipe() #Our means of communication
    self.p = mp.Process(target=self.deviceloop, args=(child_conn,))
    self.p.start()
      
  def load_settings(self):
    """Load settings for this instance of the device."""
    pass
    
  def save_settings(self):
    pass
    
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
    
  
  def quit(self):
    """This is called when the server is about to quit."""
    self.parent_conn.send('quit') #The thread (deviceloop) must understand this
    self.p.join() #or we will hang
    
  
  def interface(self):
    return
    {'initialization variables': ['address', 'port', 'authkey'],
     'input variables': None,
     'input events': None,
     'output events': {'go': 'Start the experiment by moving it from the wait phase',
                       'abort': 'Halt the experiment by moving to the wait phase',
                       'quit': 'Quit our server'}}
  
  
  def deviceloop(self, child_conn):
    """Child conn is the communication line to the other thread. remote_conn is
    the line to the client part of the controller. The server """
    keep_running = True    
    while keep_running:
      #Listen for connections on this port. Putting 'localhost' prevents 
      #connections from outside machines
      listener, remote_conn = wait_for_listener(self.address, self.port, self.authkey)
      
      while keep_running:
        if child_conn.poll():
          msg = child_conn.recv()
          if msg == 'quit':
            keep_running = False
            break
        try:
          if remote_conn.poll():
            msg = remote_conn.recv()
            child_conn.send(['device event', msg])
            time.sleep(0.01)
        except EOFError:
          logger.debug('Lost connection to client')
          listener.close()
          break
        except:
          logger.debug('Other error')
          listener.close()
          break
        
    logger.debug('Exited successfully')
        
def wait_for_listener(address, port, authkey):
  logger.debug('Waiting for client')    
  listener = None
  while listener == None:
    try:
      listener = mp.connection.Listener((address, port), authkey=authkey)
      remote_conn = listener.accept()
    except mp.AuthenticationError:
      logger.debug('Client had wrong key')
      listener.close()
      listener = None        
  logger.debug('Connection accepted from:' + listener.last_accepted[0] + ':%d' %(listener.last_accepted[1]))
  return listener, remote_conn

if __name__ == '__main__':
  #A simple text based controller for Gobesh
  from optparse import OptionParser
  from multiprocessing.connection import Client
  import sys
  sys.path.append('./Modules/') #Where all the modules live
  import keyboard

  parser = OptionParser()
  parser.add_option("-H", "--host", 
                    dest="host", default="localhost",
                    help="Hostname [%default]")
  parser.add_option("-p", "--port", 
                    dest="port", default=6000, 
                    help="Port number [%default]")
  parser.add_option("-k", "--key", 
                    dest="auth_key", default='gobesh controller', 
                    help="Authentication key [%default]")
  
  (options, args) = parser.parse_args()
  
  #address = ('localhost', 6000)#('dhc016970.med.harvard.edu', 6000)
  conn = Client((options.host, options.port), authkey=options.auth_key)
  print 'Got connection to server'
  print '(g)o'
  print '(a)bort'
  print '(q)uit'
      
  keep_running = True
  while keep_running:
    c = keyboard.getkey()
    if c == 'g':
      msg = 'go'
    elif c == 'a':
      msg = 'abort'
    elif c == 'q':
      msg = 'quit'
    else:
      msg = None
    try:
      if msg is not None:
        conn.send(msg)
        if msg =='quit':
          keep_running = False
    except:
      print 'Connection lost'
      keep_running = False

  try:
    conn.recv()
  except EOFError:
      print 'Sever exited'