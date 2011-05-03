"""Provides a device simulating eye movements. 
Commands:
Commands have to be sent as a dictionary. The dictionary must have a 'command'
key and may have optional data keys 
Commands the device responds to
start - start the device - will spit out eye positions
pause - will pause the device
quit - will shut down device and return
set - pass a dictionary that sets parameters (only while in pause mode)
      requires the key 'parameters' which contains a dictionary with the values
        'sample rate' - in Hz
        
movement - pass a dictionary that sets parameters for the movement (only
           while in run mode).  
"""


import logging
import multiprocessing as mp
import pylab

dev_log = logging.getLogger('Device')

class Device:

  def __init__(self, name = 'Sim Eye'):
    self.state = 'Pause'
    self.name = name #Our chance to name the device
    self.sample_rate = 1000 #In Hz
    
  def handles(self):
    dev_log.info('%s: initializing device' %(self.name))
    parent_conn, child_conn = mp.Pipe()
    p = mp.Process(target=self.run, args=(child_conn,))
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
        elif msg['command'] == 'quit':
          state = 'Quit'
        elif msg['command'] == 'set':#Set parameters for the eyetracker
          self.set_params(msg['params'])
  
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
            state = 'Pause'
          elif msg['command'] == 'quit':
            state = 'Quit'
          elif msg['command'] == 'set':#Set parameters for the eyetracker
            self.set_params(msg['params'])
