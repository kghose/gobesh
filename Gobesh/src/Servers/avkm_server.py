#!/usr/bin/env python
"""Need to test:
1. how to quit app
2. can we schedule polling socket and updaitng window separately
3. how to layout code - class or script?"""

"""Server that uses pyglet and pylab to generate visual stimuli. Calling this
starts up a visual stimuli server that listens for various commands and displays 
stimuli accordingly.
"""
import pyglet
import array
import pylab

from optparse import OptionParser
import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh Visual')

#Some general functions that we can import, that should eventually be moved to
#a separate module?

class VisualServer:
  """This is written as a class to allow overriding of the central logic and to
  encapsulate some persistent shared variables."""
  def __init__(self):
    self.neutral_gray = 128
    self.max_range = 127 #needs to add up to 255 or whatever resolution we use
    self.address = ''
    self.port = 6000
    self.authkey = 'visual stimuli'
    self.listener = None
    self.remote_conn = None
    
  def wait_for_client(self):
    """Wait for a client to connect and return us the connection. Putting
    'localhost' prevents connections from outside machines."""
    logger.debug('Waiting for client')
    listener = self.listener    
    while listener == None:
      try:
        listener = mp.connection.Listener((self.address, self.port), authkey=self.authkey)
        self.remote_conn = listener.accept()
        logger.debug('Connection accepted from:' + listener.last_accepted[0] + ':%d' %(listener.last_accepted[1]))
      except AuthenticationError:
        logger.debug('Client had wrong key')        

  def poll_command_server(self, dt):
    """Test if we have any messages. If so return the message, otherwise return
    None."""
    msg = None
    try: 
      if self.remote_conn.poll():
        msg = self.remote_conn.recv()
    except EOFError:
      logger.debug('Lost connection to client')
      self.listener.close()
    except:
      logger.debug('Other error')
      self.listener.close()
    return msg


  
def main():
  """If we start the server from the command line, this is the entry function."""
  options, args = parse_command_line_args()
  setup_logging(options)
  device, error = setup_stimuli_server(options)  
  if not error:
    server_loop(device, options)
  else:
    print 'There were errors setting up. Please check logging file ' + options.log_file

def parse_command_line_args():
  parser = OptionParser(version="%prog 1.0")
  parser.add_option("-d", "--debug_level", 
                    dest="debug_level", default="debug",
                    help="Set debug level. 'debug','info','warning','error','critical' [%default]")
  parser.add_option("-c", "--configuration_file", 
                    dest="configuration_file", default="demo_experiment_config.py", 
                    help="Visual stimulus configuration file to load [%default]")  
  parser.add_option("-l", "--log_file", 
                    dest="log_file", default="visualserver.log", 
                    help="Log file [%default]")
  parser.add_option("-f","--frame_rate",
                    dest="frame_rate", default=60,
                    type="int",
                    help="Display framerate in Hz [%default]")
  
  (options, args) = parser.parse_args()
  return options, args

def setup_logging(options):
  #Logging stuff
  LOG_FILENAME = options.log_file
  LEVELS = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}
  
  level = LEVELS.get(options.debug_level, logging.NOTSET)
  
  logging.basicConfig(filename=LOG_FILENAME, 
                      format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                      level=level)  

def setup_stimuli_server(options):
  """Initialize the pyglet window etc. etc."""
  device = {}
  #Put in code to read from configuration file
  window = setup_window(options)
  device['window'] = window
  
  batch = pyglet.graphics.Batch()#The list of things we gotta draw
  device['batch'] = batch
  
  return device, False

def setup_window(options):
  """If we have multiple screens setup fullscreen display on non secondary
  window, else open a window on our small screen."""  
  #http://www.pyglet.org/doc/api/pyglet.window-module.html
  display = pyglet.window.get_platform().get_default_display()
  screens = display.get_screens()
  main_screen = display.get_default_screen()
  logger.debug('Found %d screens' %(len(screens)))
  logger.debug('Main screen id is %d, specs are %s' %(main_screen.id, main_screen))
  if len(screens) > 1:
    #If we have multiple monitors us the secondary one as fullscreen display
    for screen in screens:
      logger.debug('Screen id is %d: %s' %(screen.id, screen))
    for screen in screens:
      if screen.id != main_screen.id:
        window = pyglet.window.Window(fullscreen=True, screen=screen)
        break
  else:
    window = pyglet.window.Window()

  #This code has to come AFTER the window is initialized
  #http://www.python-forum.org/pythonforum/viewtopic.php?f=2&t=11160
  # using color tuple (r,g,b,a), a is alpha value
  # rgba values are from 0.0 to 1.0
  r = g = b = float(neutral_gray)/(neutral_gray+max_range)
  bg = (r,g,b,1.0)
  pyglet.gl.glClearColor(*bg)

  return window

def setup_listener(sprite, batch):
  """http://www.pyglet.org/doc/api/pyglet.clock-module.html
  Setup things so that we listen on our open port and pass on any commands we
  get."""
  pyglet.clock.schedule_interval(listen, .5, sprite=sprite, batch=batch)
  
def listen(dt, sprite, batch):
  """Use multiprocessing to setup a listener. We use scheduling to listen to
  this port every once in a while"""
  if sprite.batch == batch:
    sprite.batch = None
  else:
    sprite.batch = batch

  
def server_loop(device, options):
  window = device['window']
  batch = device['batch']

  gabor_image = gabor_patch()
  gabor_sprite = pyglet.sprite.Sprite(gabor_image, batch=batch)

  #setup_listener(gabor_sprite, batch)

  
  @window.event
  def on_draw():
    window.clear()
    batch.draw()

  @window.event
  def on_mouse_motion(x, y, dx, dy):
    if (x <= window.width) and (y <= window.height):
      window.set_mouse_platform_visible(platform_visible=False)
    else:
      window.set_mouse_platform_visible(platform_visible=True)
            
    gabor_sprite.position = (x - gabor_sprite.width/2, y - gabor_sprite.height/2)

  @window.event
  def client_message(msg):
    print msg

  pyglet.app.run()

#Server commands
def show_sprite(name):
  """Basically move the named sprite."""
  sprite = []
  

def fixation_patch():
  I = pylab.array([255]*5*5)
  data = array.array('B', I)
  fix = pyglet.image.ImageData(width, height,'I',data.tostring())
  return fix

def gabor_patch(sigma_deg = 2,
                radius_deg = 6,
                px_deg = 50,
                sf_cyc_deg = 2,
                phase_deg = 0, #phase of cosine in degrees
                contrast = 1.0):
  """Return a gabor patch texture of the given dimensions and parameters."""

  height = width = radius_deg * px_deg
  x = pylab.linspace(-radius_deg, radius_deg, width)
  X, Y = pylab.meshgrid(x,x)
  L = pylab.exp(-(X**2+Y**2)/sigma_deg**2)#gaussian envelope
  #use around to round towards zero, otherwise you will get banding artifacts
  #dtype must be int for proper conversion to int and init of image data
  #I = pylab.array(-pylab.zeros(X.size)*max_range + neutral_gray, dtype='int')
  I = pylab.array(pylab.around(contrast*pylab.cos(2*pylab.pi*(sf_cyc_deg)*X + phase_deg*pylab.pi/180.)*L*max_range)+neutral_gray,dtype='int').ravel()
  IA = pylab.ones(I.size * 2, dtype='int')*255
  IA[:-1:2] = I#Need alpha=255 otherwise image is mixed with background
  #Data format for image http://www.pyglet.org/doc/programming_guide/accessing_or_providing_pixel_data.html
  data = array.array('B', IA)
  gabor = pyglet.image.ImageData(width, height,'IA',data.tostring())
  return gabor

if __name__ == '__main__':
  main()  