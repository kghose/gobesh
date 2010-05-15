"""Module that uses pyglet and pylab to generate visual stimuli. Calling this
module as a script (with appropriate command line arguments) starts up a visual 
stimuli server that listens for various commands and displays stimuli accordingly"""
import pyglet
import array
import pylab

from optparse import OptionParser
import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

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
                    dest="log_file", default="gobeshserver.log", 
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
  return device, False

def setup_window(options):
  """If we have multiple screens setup fullscreen display on non secondary
  window, else open a window on our small screen."""
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
  return window
  
neutral_gray = 128
max_range = 127 #needs to add up to 255 or whatever resolution we use

def server_loop(device, options):
  window = device['window']
  gabor = gabor_patch()
  sprite = pyglet.sprite.Sprite(gabor)
  
  @window.event
  def on_draw():
      window.clear()
      #label.draw()
      sprite.draw()
      #gabor.blit(0,0)
  pyglet.app.run()

def gabor_patch(sigma_deg = 2,
                radius_deg = 6,
                px_deg = 50,
                sf_cyc_deg = 2,
                phase_deg = 0, #phase of cosine in degrees
                sigma_x_deg = 2,
                sigma_y_deg = 2,
                contrast = .15):
  """Return a gabor patch texture of the given dimensions and parameters."""

  height = width = radius_deg * px_deg
  x = pylab.linspace(-radius_deg, radius_deg, width)
  X, Y = pylab.meshgrid(x,x)
  L = pylab.exp(-(X**2+Y**2)/sigma_deg)#gaussian envelope
  #use fix to round towards zero, otherwise you will get banding artifacts
  #dtype must be int for proper conversion to int and init of image data
  I = pylab.array(pylab.fix(contrast*pylab.cos(2*pylab.pi*(sf_cyc_deg)*X + phase_deg*pylab.pi/180.)*L*max_range)+neutral_gray,dtype='int').ravel()
  
  #Data format for image http://www.pyglet.org/doc/programming_guide/accessing_or_providing_pixel_data.html
  data = array.array('B', I)
  gabor = pyglet.image.ImageData(width, height,'I',data.tostring())
  return gabor


if __name__ == '__main__':
  main()  