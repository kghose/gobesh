#!/usr/bin/env python
#import multiprocessing as mp #For threading
import logging #We should make use of the logging function
logger = logging.getLogger('Gobesh.'+__name__)

import basedevice

class GAVKMDevice(basedevice.GBaseDevice):
  """Audio-Visual-Keyboard-Mouse device"""
      
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
    logger.debug('Starting device loop')  

#    keep_running = True    
#    while keep_running:
#      if child_conn.poll():
#        msg = child_conn.recv()
#        if msg == 'quit':
#          keep_running = False
#          break
  
#    import pyglet
#    w = pyglet.window.Window(resizable=True)
#    while not w.has_exit:
#      w.dispatch_events()
#    w.close()

    import avkm_server as avkms   
    device, error = avkms.setup_stimuli_server()  
    if not error:
      avkms.server_loop(device)
    else:
      print 'There were errors setting up. Please check logging file ' + options.log_file
            
    logger.debug('Exited successfully')

