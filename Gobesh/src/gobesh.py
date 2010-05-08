#!/usr/bin/env python
"""Gobesh server. Run with -h to get help. i.e
python gobesh.py -h
"""

from optparse import OptionParser
import logging
import sys
import time #For the timestamp and sleep function
if sys.platform == "win32":
  # On Windows, the best timer is time.clock()
  default_timer = time.clock
else:
  # On most other platforms, the best timer is time.time()
  default_timer = time.time


logger = logging.getLogger('Gobesh')


def quit_devices(devices):
  for device in devices:
    device.quit() #TODO: Gotta fix state_event and variables
  
def extract_variables(var_idx_list, GV):
  """Use the device definition to copy appropriate values from GV into a list
  (input_variables) to be passed to the device's polling function. We pass
  this function to the device's poll function so that the device can
  decide if it needs the inputs and only then extraction the parameters. This
  saves us computations.""" 
  variables = []
  for idx in var_idx_list:
    variables.append(GV[idx])
  return variables
  
def poll_devices(timestamp, state_event, 
                 devices, device_keys,
                 device_inputs,
                 device_outputs,
                 device_input_events, 
                 gv):
  device_events = []
  for dev_n in range(len(devices)):
  #for key in device_list.keys():
    this_device = devices[dev_n]
    state_event_for_this_device = None
    for event_conns in device_input_events[dev_n]:
      if state_event in event_conns[1]:
        state_event_for_this_device = event_conns[0]
        break
          
    this_dev_event, output_variables = \
    this_device.poll(timestamp, state_event_for_this_device, 
                     extract_variables, device_inputs[dev_n], gv)

    #If the device generated an output this polling cycle save it in the 
    #appropriate place in the global variables list
    #This works because gv is a list and is passed as reference and any
    #modifications we make to it here are passed back
    if output_variables is not None:
      for n, idx in enumerate(device_outputs[dev_n]):
        gv[idx] = output_variables[n]
    
    if this_dev_event is not None:
      device_events.append(device_keys[dev_n] + '.' + this_dev_event)
  return device_events

def parse_command_line_args():
  parser = OptionParser(version="%prog 1.0")
  parser.add_option("-d", "--debug_level", 
                    dest="debug_level", default="debug",
                    help="Set debug level. 'debug','info','warning','error','critical' [%default]")
  parser.add_option("-e", "--experiment_file", 
                    dest="experiment_file", default="controller_demo.py", 
                    help="Experiment file to load [%default]")
  parser.add_option("-l", "--log_file", 
                    dest="log_file", default="gobeshserver.log", 
                    help="Log file [%default]")
  parser.add_option("-s", "--simulate", 
                    action="store_true", dest="simulate", default=False, 
                    help="Run in simulation mode [%default]")
  parser.add_option("-t","--tick_rate",
                    dest="server_tick_rate", default=10000,
                    type="float",
                    help="Server tick rate. How many times will the server poll its devices and update the statemachine per second [%default]")
  
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

def instantiate_experiment(options):
  """Execute the experiment definition file and instantiate our device objects."""
  expt_def = {}
  error = False
  try:
    exec open(options.experiment_file)
  except:
    msg = "Error in experiment file '%s': %s" %(options.experiment_file, sys.exc_info())
    logger.error(msg)
    print msg
    error = True
    return expt_def, error
  
  expt_def['state machine'] = StateMachine  
  
  gv, gv_keys = initialize_global_variables(GlobalVariableDefinitions)
  expt_def['global variables'] = gv
  expt_def['global variable keys'] = gv_keys
    
  dev_key_list = DeviceDefinitions.keys()
  dev = []  
  initvars = []
  inputs = []
  outputs = []
  input_events = []
  # Device instantiation has to be done in the same namespace as the
  # exec open(options.experiment_file) command since the 'import' statements
  # in the experiment file apply to that namespace only
  for dev_key in dev_key_list:
    this_device = None
    try:
      this_device = eval(DeviceDefinitions[dev_key]['class'] + '()')
    except:
      error = True
      logger.error('Device %s has no class definition' %(dev_key))
    else:
      init_var_idx_list, input_var_idx_list, output_var_idx_list, input_event_list, error = \
        setup_device(dev_key, DeviceDefinitions, gv_keys)
      dev.append(this_device)
      initvars.append(init_var_idx_list)
      inputs.append(input_var_idx_list)
      outputs.append(output_var_idx_list)
      input_events.append(input_event_list)

  expt_def['device keys'] = dev_key_list
  expt_def['device list'] = dev
  expt_def['device init vars'] = initvars
  expt_def['device inputs'] = inputs
  expt_def['device outputs'] = outputs
  expt_def['device input events'] = input_events

  return expt_def, error

def initialize_global_variables(GVD):
  """Turns global variable definitions into a list for quicker access. This is 
  important because we have to extract the appropriate variables from the
  global space and pass it to the device, potentially, every poll cycle.
  Dictionaries are easier for humans to read but carry more overhead. Since our
  design does not call for new keys to be inserted on the fly, we simply convert
  the dictionary into a list and keep a list of keys handy so we know what is
  what"""
  gv = []
  gv_key_list = GVD.keys()
  for key in gv_key_list:
    gv.append(GVD[key])
  return gv, gv_key_list

#TODO: Where to put variable initialization?
def setup_device(dev_key, DeviceDefinitions, gv_keys):
  """Given the device definition, figure out which global variables are inputs
  and outputs, what the events are and what the initialization variables are"""
  error = False

  input_var_idx_list = []
  if DeviceDefinitions[dev_key].has_key('input variables'):
    input_keys = DeviceDefinitions[dev_key]['input variables']
    if input_keys is not None:
      for var_key in input_keys:
        try:    
          key_idx = gv_keys.index(var_key)
          input_var_idx_list.append(key_idx)
        except ValueError:
          logger.error('Device %s wants non existent variable %s for input' %(dev_key, var_key))
          error = True    
  else:
    error = True
    logger.error('Device %s has no input variable definition' %(dev_key))
  
  init_var_idx_list = []#TODO:
  
  output_var_idx_list = []    
  if DeviceDefinitions[dev_key].has_key('output variables'):
    ouput_keys = DeviceDefinitions[dev_key]['output variables']
    if ouput_keys is not None:
      for var_key in ouput_keys:
        try:    
          key_idx = gv_keys.index(var_key)
          output_var_idx_list.append(key_idx)
        except ValueError:
          error = True          
          logger.error('Device %s wants non existent variable %s for output' %(dev_key, var_key))        
  else:
    error = True
    logger.error('Device %s has no output variable definition' %(dev_key))
  
  input_event_list = []
  if DeviceDefinitions[dev_key].has_key('input events'):
    input_event_def = DeviceDefinitions[dev_key]['input events']
    if input_event_def is not None:
      for event_key in input_event_def.keys():
        input_event_list.append([event_key, input_event_def[event_key]])
  else:
    error = True
    logger.error('Device %s has no output variable definition' %(dev_key))
     
  return init_var_idx_list, input_var_idx_list, output_var_idx_list, input_event_list, error

def initialize_devices(devices, device_init_vars, gv):
  for n in range(len(devices)):
    init_vars = extract_variables(device_init_vars[n], gv)
    devices[n].initialize(init_vars)
  
def server_loop(options, expt_def):
  error = False
  #unbundle the expt_def dictionary for speedy access in the polling loop
  state_machine = expt_def['state machine']
  gv_keys = expt_def['global variable keys']
  gv = expt_def['global variables']
  device_keys = expt_def['device keys']
  devices = expt_def['device list']
  device_init_vars = expt_def['device init vars']
  device_inputs = expt_def['device inputs']
  device_outputs = expt_def['device outputs']
  device_input_events = expt_def['device input events']
  
  tick_interval = 1.0/options.server_tick_rate#Server tick rate

  initialize_devices(devices, device_init_vars, gv)
  
  device_event_queue = []
  state_event_queue = [] #Events emitted by states
  
  state = 'Wait' #Built in start state
  timestamp = default_timer()
  while state != 'Exit' and not error: #last state
    timestamp = default_timer()
    
    #Poll devices
    if len(state_event_queue) > 0:
      this_state_event = state_event_queue.pop(0)
    else:
      this_state_event = None
    these_device_events = poll_devices(timestamp, this_state_event, 
                 devices, device_keys,
                 device_inputs,
                 device_outputs,
                 device_input_events, 
                 gv)
    if len(these_device_events) > 0:
      device_event_queue += these_device_events
    if len(device_event_queue) > 0:
      this_event = device_event_queue.pop(0)    
      if state_machine[state].has_key(this_event):
        state_event_queue.append(state + '.exit')
        state = state_machine[state][this_event]
        state_event_queue.append(state + '.enter')
      print this_event, state
    else:
      time.sleep(tick_interval)
  
  #print state_events
  quit_devices(devices)
  if error:
    print 'There were errors'  
 
    
def main():
  options, args = parse_command_line_args()
  setup_logging(options)
  expt_def, error = instantiate_experiment(options)
  if not error:
    server_loop(options, expt_def)
  else:
    print 'There were errors setting up. Please check logging file ' + options.log_file

if __name__ == '__main__':
  main()