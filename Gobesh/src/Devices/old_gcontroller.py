"""This module provides the basic controller device. It also provides a simple
text based front end for testing."""

import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

#Imports for this device
import basedevice
import time #For the sleep function
import keyboard

class GController(basedevice.GBaseDevice):
  """A general controller device we can use in our experiments"""

  def setup_interface(self):
    

  def get_settings(self):
    return {'address': [self.address, True],
            'port': [self.port, True],
            'authkey': [self.authkey, True]}
  
  def set_settings(self, vars):
    self.address = vars.get('address','')
    self.port = vars.get('port',6000)
    self.authkey = vars.get('authkey','gobesh controller')
    
  
  def deviceloop(self):
    """."""
    logger.debug('Starting device loop')
    keep_running = True
    while keep_running:
      if not self.queue_from_parent.empty()
        msg = self.queue_from_parent.get()
        if msg[0] == 'variable':
          #Code to handle variable exchange
          #var_name = msg[1]
          #var_value = msg[2]
        elif msg[0] == 'event':
          #Code to handle events
          event_name = msg[1]
          if event_name == 'quit':
            keep_running = False
        
        elif msg[0] == 'get settings':
          #Return us a dictionary of variables, with values and whether they
          #are readonly
          settings_dict = self.get_settings()
          self.queue_to_parent.put([self.name, 'settings', settings_dict])
          
        elif msg[0] == 'set settings':
          #We have been given new settings
          self.set_settings(msg[1])
            
        elif msg[0] == 'time stamp':
          #Handle time stamping
          #time_stamp = msg[1]
             
      #Code for main device operations goes here

      #Listen for connections on this port. Putting 'localhost' prevents 
      #connections from outside machines
      listener, remote_conn = wait_for_listener(self.address, self.port, self.authkey)


      
    logger.debug('Exited device loop')








    
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