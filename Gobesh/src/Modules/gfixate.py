"""An device that takes in a fixation window center and radius and sends out an
event called 'fixate' if the eye position is within the fixation circle.

Debouncing: Internally gfixate tracks whether each sample is within the fixation
window or not. It only emits an event when the samples consistently indicate a
state change for longer than the debounce time. When the device is first started
its internal state is 'not fixating'. If the eye xy is within the fixation 
radius for longer than debounce_ms then the internal state switches to 
'fixating', and the 'fixate' event is emitted. If the eye xy now moves out of 
the fixation window and remains out for more than debounce_ms then the internal
state changes to 'not fixating' and the 'no fixate' event is emitted."""

import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

class GFixate:
  """."""
  def __init__(self):
    #The interface for the class
    #Can be accessed by calling .interface
    #Useful for humans, not used in the code
    self.interface = \
    {'initialization variables': None,
     'input variables': {'eye xy':'x,y tuple of eye position',
                         'debounce ms':'Ignore change of state that occurs faster than this', 
                         'fix xy':'fixation window center',
                         'fix r':'fixation window radius'},
     'output variables': None,
     'input events': None,
     'output events': {'fixate':'Output whenever eye position enters window',
                       'no_fixate':'Output whenever eye position leaves window'}}
      
  def initialize(self, vars):
    """This is called when the server initializes."""
    self.fix_xy = vars.get('fix xy',(0,0))
    self.fix_r = vars.get('fix r',2)
    self.fixating = False
    self.timer_ms = 0
    #This device has a light enough load that we can put the work in the main
    #loop. We do this because the computation is probably about as light as the
    #polling overhead
    #self.parent_conn, child_conn = mp.Pipe()
    #self.p = mp.Process(target=self.deviceloop, args=(child_conn,))
    #self.p.start()
  
  def quit(self):
    """This is called when the server is about to quit. This device has no
    threads to terminate, and nothing to clean up."""

  def poll(self, timestamp, state_event, input_vars):
    """This is the call that is visible to the main loop. The main loop calls
    this each time it loops. This is a light device, so all the work is done
    in the poll method itself."""
    output_variables = None
    device_event = None
        
    if input_vars is not None:
      self.fix_xy = input_vars.get('fix xy', self.fix_xy)
      self.fix_r = input_vars.get('fix r', self.fix_r)
      eye_xy = input_vars.get('eye xy', None)
      if eye_xy is not None:
        dx = eye_xy[0] - fix_xy[0]
        dy = eye_xy[1] - fix_xy[1]
        if (dx**2 + dy**2) - fix_r**2 > 0:#Out of fixation box
          if self.fixating:
            #We are fixating, so we gotta start timing to see if this is 
            #XXXX TODO
          device_event = 'no fixate'
        else:
          device_event = 'fixate'
        
    return device_event, output_variables