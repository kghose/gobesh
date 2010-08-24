"""This module provides an example device that illustrates the API that has to
be exposed to Gobesh."""

import multiprocessing as mp #For threading
import logging #We should make use of the logging function
logger = logging.getLogger('Gobesh.'+__name__)
from gobesh_lib import import default_timer

class GBaseDevice:
  """This base device can be inherited by classes that implement devices, or 
  the 'hook' part of external devices."""
  def __init__(self):
    """Use this to do any fixed initialization. This is called when the server
    (main loop) instantiates the device objects"""
    pass
  
  def initialize(self, config_dir = './'):
    """This is called when the main loop initializes all the devices. It is
    done once at startup, and again if the server is told to perform a reset.
    This should return the device to an initial state.
    Gobesh will pass it a directory where it can store/load settings however it 
    wishes (though python's configuration file method is recommended).
    The device should be able to make up default settings if no file is found.
    It loads settings from the settings file, sets up IPC with the child process 
    and then starts the child process. 
    If the operations the device does are non-blocking (quick computations
    for example) you may omit the deviceloop thread, override this function and
    have all the logic in the poll function. Remember to put sensible values
    for the latency tracking gobesh does.
    For devices that do operations in the deviceloop thread it may be easiest
    to keep this function as it is.
    For hooks (devices running separately as a server, with gobesh interacting
    via a socket) the deviceloop may also be omitted and the poll loop may 
    consist of poll() commands that send and recieve data via the socket. In
    that case initialize is used to probe for and make connections to the
    server."""
    #self.generate_config_fname(config_dir, my_name)
    self.config_dir = config_dir
    self.load_settings()

    #Fixed code that should be same for all devices that start a child thread
    self.parent_conn, child_conn = mp.Pipe() #Our means of communication
    self.p = mp.Process(target=self.deviceloop, args=(child_conn,))
    self.p.start()
          
  def load_settings(self):
    """Load settings for this instance of the device. The directory to put
    the configuration file is in self.config_dir"""
    pass
    
  def save_settings(self):
    pass
    
  def poll(self, timestamp, state_event, input_vars):
    """This is the call that is visible to gobesh (main loop). Gobesh calls
    this each time it loops. 
    
    timestamp - is obtained using the default_timer() function and sent in by
                gobesh. This is sent in every poll period and the device 
                can choose to use it as a synch signal.
                Gobesh sends in a fresh time stamp for each call of poll.
                
    state_event - any state event(s) that this device is hooked up to. Sent as
                  a list of strings
                  
    input_vars  - any input variables that this device is hooked up to 
    
    This function should be non-blocking. Minor computations can be done here
    but anything major or I/O that should be running in its own time should
    run in a different thread. In such cases this function should be a conduit
    to deviceloop
    
    The return value should be the event that the device returns.
    """
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
    try:
      self.parent_conn.send('quit') #The thread (deviceloop) must understand this
      self.p.join() #or we will hang
    except AttributeError:
      pass
    else:
      raise
    
    save_settings()
    
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
    the line to the client part of the controller. 
    Functions of the deviceloop:
    1. Keep a record of command latencies. Command latencies are measured from
    the time the 'poll' command sent in a state transition to the time at which
    the device acknowledges the command. For devices where the work is done in
    the device loop this is computed in the device loop itself (as shown here).
    For devices where the work is done in a separate process and the device
    loop merely communicates with
    
    The server"""
    logger.debug('Starting device loop')  
    ping_interval_s = 1
    last_ping_at = default_timer()
    
    keep_running = True
    while keep_running:
      if child_conn.poll():
        msg = child_conn.recv()
        time_msg_recvd = default_timer()
        if time_msg_recvd - last_ping_at >= ping_interval:
          last_ping_at = time_msg_recvd
          child_conn.send(['latency ms', latency_ms]) 
        
        if msg == 'quit':
          keep_running = False
          logger.debug('Received quit instruction')
          break


    logger.debug('Exited successfully')