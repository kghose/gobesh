"""Provides an example of an input device class for gobesh. An source device 
"""

import logging
import multiprocessing as mp
import pylab

dev_log = logging.getLogger('InputDevice')

class InputDevice:

  def __init__(self, name = 'Device'):
    self.state = 'Pause'
    self.name = name #Our chance to name the device
    dev_log.info('%s: initializing device' %(self.name))
    self.parent_conn, child_conn = mp.Pipe()
    self.p = mp.Process(target=self.run, args=(child_conn,))

  def initialize(self, params):
    """Any initialization that can only be done when device is in pause mode."""
    self.parent_conn()
  
  
  def command(self, cmd):
    """."""
    
  def poll(self):
  
    
    
  def handles(self):
    return parent_conn, p
  
  def run(self,conn):
    
    
    #State system switch yard
    state = self.state
    while True:
      if state == 'Pause':
        dev_log.info('%s: in wait mode' %(self.name))
        conn.poll(None)#Wait indefinitely
        msg = conn.recv()
        if msg['command'] == 'start': #Will crash if msg not correct format, that's OK
          dev_log.info('%s: switching to start mode' %(self.name))          
          state = 'Run'
        if msg['command'] == 'quit':
          state = 'Quit'
      elif state == 'Quit':
        dev_log.info('%s: quitting' %(self.name)) 
        #Shut down and quit
        break
      elif state == 'Run':
        #Do what we have to do, which sometimes means send data
        r = pylab.randn()
        if r > 2.0:
          conn.send(pylab.randn(1))#randomly send out some data
        #Check if we are being told something
        if conn.poll():
          msg = conn.recv()
          if msg['command'] == 'pause':
            state = 'Wait'
          elif msg['command'] == 'quit':
            state = 'Quit'
