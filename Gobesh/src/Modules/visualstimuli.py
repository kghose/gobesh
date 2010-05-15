"""Module that uses pyglet and pylab to generate visual stimuli. Calling this
module starts up a visual stimuli server that listens for various commands
and displays stimuli accordingly"""
import pyglet
import array
import pylab

from optparse import OptionParser
import multiprocessing as mp
import logging
logger = logging.getLogger('Gobesh.'+__name__)

def main():
  options, args = parse_command_line_args()
  setup_logging(options)
  expt_def, error = instantiate_experiment(options)
  return
  if not error:
    error = initialize_devices(options, expt_def)
  if not error:
    server_loop(options, expt_def)
  else:
    print 'There were errors setting up. Please check logging file ' + options.log_file

def parse_command_line_args():
  parser = OptionParser(version="%prog 1.0")
  parser.add_option("-d", "--debug_level", 
                    dest="debug_level", default="debug",
                    help="Set debug level. 'debug','info','warning','error','critical' [%default]")
  parser.add_option("-e", "--experiment_file", 
                    dest="experiment_file", default="demo_experiment.py", 
                    help="Experiment file to load [%default]")
  parser.add_option("-c", "--configuration_file", 
                    dest="configuration_file", default="demo_experiment_config.py", 
                    help="Configuration file to load [%default]")  
  parser.add_option("-l", "--log_file", 
                    dest="log_file", default="gobeshserver.log", 
                    help="Log file [%default]")
  parser.add_option("-s", "--simulate", 
                    action="store_true", dest="simulate", default=False, 
                    help="Run in simulation mode [%default]")
  parser.add_option("-t","--tick_interval",
                    dest="server_tick_interval", default=10,
                    type="float",
                    help="Server tick interval (sleep between polls) in ms [%default]")
  
  (options, args) = parser.parse_args()
  return options, args


neutral_gray = 128
max_range = 127 #needs to add up to 255 or whatever resolution we use

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