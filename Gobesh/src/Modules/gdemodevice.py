"""This is a demo device that illustrates how to write a device."""

import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

#Imports for this device
import time #For the sleep function
import random

class GDemoDevice:
  """This device does EVERYTHING. And nothing"""
  def __init__(self):
    #The interface for the class
    #Can be accessed by calling .interface
    #Useful for humans, not used in the code
    self.interface = \
    {'initialization variables': ['w'],
     'input variables': ['a','b'],
     'output variables': ['x', 'y'],
     'input events': {'eventin1': 'One event',
                      'eventin2': 'Another event'},
     'output events': {'eventout1': 'One event',
                       'eventout2': 'Another event'}}
      
  def initialize(self, init_variables):
    """This is called when the server initializes."""
    print 'Initialization variables', init_variables
    self.parent_conn, child_conn = mp.Pipe()
    self.p = mp.Process(target=self.deviceloop, args=(child_conn,))
    self.p.start()
  
  def quit(self):
    """This is called when the server is about to quit."""
    self.parent_conn.send(['command','quit']) #The thread (deviceloop) must understand this
    self.p.join() #or we will hang
    
  def poll(self, timestamp, state_event, input_variables):
    """This is the call that is visible to the main loop. The main loop calls
    this each time it loops."""
    #This is for illustration. Typically we would not hold up the thread with
    #computations
    a = input_variables[0]
    b = input_variables[1]
    output_variables = None
    
    device_event = None
    if self.parent_conn.poll():
      #We have a message
      msg = self.parent_conn.recv()
      if msg[0] == 'device event':
        if msg[1] == '1':
          device_event = 'eventout1'
        if msg[1] == '2':
          device_event = 'eventout2'
      if msg[0] == 'data request':
        self.parent_conn.send(['data',[a,b]])
      if msg[0] == 'data':
        output_variables = [msg[0][0], msg[0][1]]
        
    return device_event, output_variables
  
  def deviceloop(self, child_conn):
    """This is the function that runs in the other thread. 
    Child conn is the communication line to the other thread."""
    keep_running = True
    
    while keep_running:
      r = random.randint(0,50)
      if r == 0:
        child_conn.send(['device event','1'])
      if r == 50:
        child_conn.send(['device event','2'])
      if r == 25:
        child_conn.send(['data request'])
      
      if child_conn.poll():
        msg = child_conn.recv()
        if msg[0] == 'command':
          if msg[1] == 'quit':
            keep_running = False
        if msg[0] == 'data':
          a = msg[1][0]
          b = msg[1][1]
          x = a - b
          y = a + b
          child_conn.send(['data',[x,y]])
      time.sleep(0.01)