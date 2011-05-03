"""Custom modules for the Lorentz experiment."""
#Or define it right here
class Controller(GBaseDevice):
  """."""
  def setup_interface(self):
    self.interface = 
    {'device name': 'Lorentz Controller',
     'description': 'Controller device for the Lorentz experiment'
     'input variables': {
         'sigma': 'f'                },
     'output variables': {},
     'input events': [],
     'output events': []}
    
      
  def deviceloop(self):
    """."""
    logger.debug('Starting device loop')
    self.keep_running = True
    while self.keep_running:
      if not self.queue_from_parent.empty()
        self.route_input()
        self.event_handler()
      
      #Code for main device operations goes here
      
    logger.debug('Exited device loop')

  def event_handler(self):
    """Reimplement this as needed."""
    if self.event_name == 'quit':
      self.keep_running = False
