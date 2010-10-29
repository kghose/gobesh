"""This module provides an example device that illustrates the API that has to
be exposed to Gobesh."""

import multiprocessing as mp #For threading
import logging #We should make use of the logging function
logger = logging.getLogger('Gobesh.'+__name__)

class GBaseDevice():
  """This base device can be inherited by classes that implement devices, or 
  the 'hook' part of external devices. In most cases it will be sufficient to
  reimplement the eventhandler method and the DeviceInterface."""
  
  def __init__(self, name, queue_to_parent):
    """This is called when the server (main loop) instantiates the device objects.
    name - unique string among all the other names in the experiment
    queue_to_parent - a queue onto which the device puts data and events
    """
    self.name = name
        
    #Any data/events produced by the deviceloop will be put on this queue
    #and be consumed by the main thread as required 
    self.queue_to_parent = queue_to_parent

    #Any data/events routed to the device from the statemachine or other devices
    #by the main thread    
    self.queue_from_parent = mp.Queue() 
  
    #This allows the main thread to perform some variable read/writes without
    #having to go through the queues
    self.lock = mp.Lock()
    
    self.setup_interface()
    self.init_variables()
    
  def start(self):
    self.p = mp.Process(target=self.deviceloop)
    self.p.start()

  def stop(self):
    if hasattr(self,p):
      self.queue_from_parent.put(['event','quit'])
      self.p.join() #this could hang, maybe do timeout and terminate?
      logger.debug('Successfully stopped')
    else:
      logger.debug('deviceloop not started yet')
        
  def restart(self):
    """."""  
    self.stop()
    self.start()
    logger.debug('Restarted')    
                        
  def quit(self):
    self.stop()
  
  def init_variables(self):
    """Use self.interface to setup and initialize variables."""
    for kv in self.interface['input variables']:
      self.__dict__[kv[0]] = kv[5]
     
  def get_settings(self):
    """Return a dictionary of settable variables and triggerable events.
    Each list 
    """
    vars = []
    settable = self.interface['input variables']
    self.lock.acquire()
    for kv in settable:
      if kv[3] == True:#Visible to user
        #var name, description, type, editable, value 
        vars.append([kv[0], kv[1], kv[2], kv[4], self.__dict__[kv[0]]])
    self.lock.release()
        
    events = []
    settable = self.interface['input events'] 
    for kv in settable:
      if kv[2] == True:#User triggerable
        #event name, description
        events.append([kv[0], kv[1]])
    
    settings = {'variables': vars, 'events': events}
    return settings
  
  def set_variables(self, vars):
    """Copy values from settings_dict into class variables if we allow it.
    vars is a list of lists. Each sub list consists of the variable name,
    and the variable value"""
    settable = self.interface['input variables']
    self.lock.acquire()
    for kv in vars:
      for kv_set in settable:
        if (kv[0] == kv_set[0]):
          if kv_set[4] and self.__dict__.has_key(kv[0]):
            if kv_set[2] == 'f':
              self.__dict__[kv[0]] = float(kv[1])
            else:
              self.__dict__[kv[0]] = kv[1]
          break #Breaks us out of kv_set loop
    self.validate_variables()#User defined, if needed
    self.lock.release()
    
          
  #Reimplement the following functions as needed
  def setup_interface(self):
    """Create a dictionary that describe the device and its interface. This is 
    useful for documentation, when we want to know what are the inputs and 
    outputs for the device.
    
    This dictionary is consulted when the experiment is being instantiated and
    the device hook ups are checked for validity.
        
    1. 'device name' - A name for this class of device
    2. 'description' - an english language description for this device 
    3. 'input variables' - can consume variables produced by other devices.
       [var name, string description, data type, visible to user, modifiable via interface T/F, default value] 
       data type can be:
        'f' for numberic, passed as float
        's' for string
    4. 'output variables' - produced by the device and can be routed to other devices
       string description
    5. 'input events' - can be triggered by statemachine events
       [string description, triggerable via user interface T/F]
    6. 'output events' - can be hooked up to change state machine state.
       string description
    These are lists because we want to maintain an order for display purposes
       
    Note that, for controlling the device, we are free to set up more complex 
    interfaces. This interface description is used by the built in gobesh server 
    to produce a basic control panel for the device.
    
    The base device doubles as a simple working device to test out Gobesh
    """
    self.interface = \
    {'device name': 'Base Device',
     'description': 'Base device with examples of how to do things',
     'input variables': [['dx','dx', 'f', False, False, 0], 
                         ['dy','dy', 'f', False, False, 0], 
                         ['dz','dz', 'f', False, False, 0],
                         ['rate','rate (Hz)', 'f', True, True, 200],
                         ['sigma', 'sigma', 'f', True, True, 10], 
                         ['rho', 'rho', 'f', True, True, 28], 
                         ['beta', 'beta', 'f', True, True, 2.66]],
     'output variables': [['x','x'], ['y','y'], ['z','z'], 
                          ['dx', 'dx'], ['dy', 'dy'], ['dz', 'dz']],
     'input events': [['perturb', 'Perturb the x,y,z value randomly', True]],
     'output events': [['random_event', 'An event generated randomly']]}
  
  def validate_variables(self):
    """Reimplement this if we need to check parameter settings for sanity."""
    pass
            
  def deviceloop(self):
    """The details of this method will differ from device to device."""
    logger.debug('Starting device loop')
    keep_running = True
    while keep_running:
      if not self.queue_from_parent.empty():
        msg = self.queue_from_parent.get()
        if msg[0] == 'variable':
          #Code to handle variable exchange
          var_name = msg[1]
          var_value = msg[2]
        elif msg[0] == 'event':
          #Code to handle events
          event_name = msg[1]
          if event_name == 'quit':
            keep_running = False
                  
            
        elif msg[0] == 'time stamp':
          #Handle time stamping
          time_stamp = msg[1]
          
      #Code for main device operations goes here
      pass
    
    logger.debug('Exited device loop')

    