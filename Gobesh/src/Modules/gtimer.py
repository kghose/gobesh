"""A timer. A common device used in experiments"""
import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

#Imports for this device
import sys
import time

class GTimer:
  def __init__(self):
    #The interface for the class
    #Can be accessed by calling .interface
    self.interface =
    {'input variables': {'time_ms': {'default':100, 'help':'Time to count down in ms'}},
     'input events': {'start': 'Start the timer'},
      'output events': {'done': 'Timer has finished countdown'}}

  if sys.platform == "win32":
      # On Windows, the best timer is time.clock()
      self.default_timer = time.clock
  else:
      # On most other platforms, the best timer is time.time()
      self.default_timer = time.time
      
  def initialize(self, variables):
    """This is called when the server initializes."""
    self.parent_conn, child_conn = mp.Pipe()
    self.p = Process(target=deviceloop, args=(child_conn,))
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
    device's loop returns."""

    if state_event == 'start':#The only event we understand
      self.parent_conn.send(['set timer',variables['time_ms']])
      self.parent_conn.send(['state event', state_event])
    
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
    timer_started = False
    start_time = self.default_timer()
    time_s = 0
    #Do initialization here
    while keep_running:
      if child_conn.poll():
        msg = child_conn.recv()
        if msg[0] == 'set timer':
          time_s = msg[1]*1000
        if msg[0] == 'state event':
          if msg[1] == 'start':
            timer_started = True
            start_time = self.default_timer()
        if msg[0] == 'quit':
          #This device has a trivial exit
          keep_running = False
      
      if timer_started:
        current_time = self.default_timer()
        if current_time - start_time >= time_s:
          timer_started = False
          child_conn.send(['device event', 'done'])
          
    #No clean up needed during exit