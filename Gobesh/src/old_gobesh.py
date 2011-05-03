#!/usr/bin/env python
"""Gobesh core
"""

from optparse import OptionParser
import logging
import sys
import time #For the timestamp and sleep function

from gobesh_lib import import default_timer

logger = logging.getLogger('Gobesh')


def ping_devices():
  """Execute the ping function for each device to get an estimate of the
  transmission latency between gobesh and the device."""
  
def synch_pulse():
  """Execute the synch function for each device so that each device has data
  on the skew between its clock and the central clock."""


def generate_config_fname(self, config_dir = './', my_name = 'ADemoDevice'):
  """The convention is to keep settings for each device in a separate file
  under a root directory specified by gobesh (which gobesh gets as a command 
  line argument). The settings file name is derived from the class and instance 
  names for the device as seen in this method"""
  self.config_fname = config_dir + self.__name__ + my_name + '.cfg'

def quit_devices(devices):
  for device in devices:
    device.quit() #TODO: Gotta fix state_event and variables
  
def poll_devices(timestamp, #Pass this to device poll to allow them to synch time stamps with main server 
                 state_event, #State event from the stack
                 last_variables, #Variables generated last poll                 
                 devices, device_keys, #Allows us access to the devices
                 se_dict #maps state events to recipient devices
                 ):
  input_state_events = se_dict.get(state_event, se_dict['__NOEVENT__'])
  device_events = [] #events produced by devices this poll
  variables_produced = {} #variables produced this poll
  for dev_n in range(len(devices)):
  #for key in device_list.keys():
    this_device = devices[dev_n]
    state_event_for_this_device = input_state_events[dev_n]
    this_dev_event, this_dev_output = \
    this_device.poll(timestamp, state_event_for_this_device, {})

    #If the device generated an output this polling cycle save it in the 
    #appropriate place in the global variables list
    #This works because gv is a list and is passed as reference and any
    #modifications we make to it here are passed back
    if this_dev_output is not None:
      variables_produced[device_keys[dev_n]] = this_dev_output
    
    if this_dev_event is not None:
      device_events.append(device_keys[dev_n] + '.' + this_dev_event)
  return device_events, variables_produced

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

#def build_state_event_dictionary_old(DeviceDefinitions, dev_key_list):
#  """Given the device definitions build up a state event dictionary that will
#  allow us to map a given state event to the appropriate device input events.
#  Each key of the state event dictionary corresponds to an event we want to
#  process (a string of the form statename.enter or statename.exit). The value for
#  a key is a list of lists. The nth element of the list is passed to the nth
#  device in the dev_key_list. This element is itself a list of names of events
#  for that device triggered by the state event.
#  """
#  se_dict = {'__NOEVENT__':[[] for n in range(len(dev_key_list))]}
#  for dev_idx, dev_key in enumerate(dev_key_list):
#    if DeviceDefinitions[dev_key].has_key('input events'):
#      input_event_def = DeviceDefinitions[dev_key]['input events']
#      if input_event_def is not None:
#        for event_key in input_event_def.keys():
#          for se in input_event_def[event_key]:
#            if se_dict.has_key(se):
#              se_dict[se][dev_idx].append(event_key)
#            else:
#              se_dict[se] = [[] for n in range(len(dev_key_list))]
#              se_dict[se][dev_idx] = [event_key]
#    else:
#      logger.warning('Device %s has no input event definitions' %(dev_key))
#  logger.debug(se_dict)
#  return se_dict  

def build_state_event_dictionary(DeviceDefinitions):
  """Given the device definitions build up a state event dictionary that will
  allow us to map a given state event to the appropriate device input events.
  Each key of the state event dictionary corresponds to a state event that at
  least one device uses (a string of the form statename.enter or statename.exit). 
  The value for each event key is a dictionary with keys corresponding to the
  devices that should receive that event.
  Each value to those keys is a list of strings corresponding to the input
  events of that device (in principle there can be more than one) that are
  hooked up to this state event.
  """
  se_dict = {}
  for dev_key in DeviceDefinitions.keys():#go through all the devices
    if DeviceDefinitions[dev_key].has_key('input events'):#If skipped, warn user
      input_event_def = DeviceDefinitions[dev_key]['input events']
      if input_event_def is not None:
        #Cycle through the hooked up state event inputs for this device
        for event_key in input_event_def.keys():
          #Cycle through the state events that trigger this device event 
          #(there can be more than one)
          for se in input_event_def[event_key]:
            #We might already have this state event in our dictionary
            if se_dict.has_key(se):
              #Now we have to see if we have this device associated with this
              #event
              if se_dict[se].has_key(dev_key):
                #We just append it in  
                se_dict[se][dev_key].append(event_key)
            else:
              #We don't have this device key.    
              se_dict[se][dev_key] = [event_key]
    else:
      logger.warning('Device %s has no input event definitions' %(dev_key))
  #logger.debug(se_dict)
  return se_dict


def build_variables_dictionary(DeviceDefinitions):
  """Given the device definitions build up a variables dictionary that will
  allow us to map production of a given variable to the appropriate inputs in
  the devices. 
  Each key of the variable dictionary is a variable name at least one device 
  wants. 
  The value for each variable key is a dictionary. The keys to this dictionary
  are the devices the variable needs to be routed to.
  The value for each device key is a list of input variables for that device 
  (in principle there can be more than one) that the variable needs to be routed to in this
  device.
  """
  var_dict = {'__NOVARS__':[None]*len(dev_key_list)}
  for dev_idx, dev_key in enumerate(dev_key_list):
    if DeviceDefinitions[dev_key].has_key('input variables'):
      input_var_def = DeviceDefinitions[dev_key]['input variables']
      if input_var_def is not None:
        for consumer_var_key in input_var_def.keys():
          producer_var_key = input_var_def[consumer_var_key]
          if var_dict.has_key(producer_var_key):
            var_dict[producer_var_key][dev_idx].append(consumer_var_key)
          else:
            var_dict[producer_var_key] = [[] for n in range(len(dev_key_list))]
            var_dict[producer_var_key][dev_idx] = consumer_var_key
    else:
      logger.warning('Device %s has no input event definitions' %(dev_key))
  logger.debug(var_dict)
  return var_dict  
  
def instantiate_experiment(StateMachine, DeviceDefinitions):
  """Execute the experiment definition file and instantiate our device objects,
  create our state event and variable routing dictionaries."""
  
  expt_def['state machine'] = StateMachine  

  if DeviceDefinitions.has_key('__NODEVICE__'):
    msg = "Device can not have name __NODEVICE__"
    logger.error(msg)
    print msg
    error = True
    return expt_def, error    
  expt_def['device keys'] = dev_key_list = DeviceDefinitions.keys()
  expt_def['state event dictionary'] = build_state_event_dictionary(DeviceDefinitions, dev_key_list)
  expt_def['variable routing dictionary'] = build_variables_dictionary(DeviceDefinitions, dev_key_list)
  
  dev = []  
  # Device instantiation has to be done in the same namespace as the
  # exec open(options.experiment_file) command since the 'import' statements
  # in the experiment file apply to that namespace only
  for dev_key in dev_key_list:
    this_device = None
    try:
      this_device = DeviceDefinitions[dev_key]['class']()
    except:
      error = True
      logger.error('Problem with Device %s class instantiation' %(dev_key))
    else:
      dev.append(this_device)

  expt_def['device list'] = dev

  return expt_def, error

def initialize_devices(options, expt_def):
  error = False
  try:
    exec open(options.configuration_file)
  except:
    msg = "Error in configuration file '%s': %s" %(options.configuration_file, sys.exc_info())
    logger.error(msg)
    print msg
    error = True
  else:
    device_keys = expt_def['device keys']
    devices = expt_def['device list']
    for n in range(len(devices)):
      devices[n].initialize(DeviceConfiguration.get(device_keys[n]))
  return error

def server_loop(options, expt_def):
  error = False
  #unbundle the expt_def dictionary for speedy access in the polling loop
  state_machine = expt_def['state machine']
  device_keys = expt_def['device keys']
  devices = expt_def['device list']
  se_dict = expt_def['state event dictionary']
  
  tick_interval = options.server_tick_interval * tick_multiplier#/1000.#need it in s
  print tick_interval
    
  device_event_queue = []
  state_event_queue = [] #Events emitted by states
  variables_produced = {} #Variables to pass to relevant devices
  
  total_loops = 0
  state = 'Wait' #Built in start state
  starttimestamp = default_timer()#init the clock (needed mostly for windows)
  while state != 'Exit' and not error: #last state
    timestamp = default_timer()
    total_loops += 1
    
    #Poll devices
    if len(state_event_queue) > 0:
      this_state_event = state_event_queue.pop(0)
    else:
      this_state_event = None
    these_device_events, variables_produced = \
    poll_devices(timestamp, 
                 this_state_event,
                 variables_produced, 
                 devices, device_keys,
                 se_dict)
    if len(these_device_events) > 0:
      device_event_queue += these_device_events
    if len(device_event_queue) > 0:
      this_event = device_event_queue.pop(0)    
      if state_machine[state].has_key(this_event):
        state_event_queue.append(state + '.exit')
        state = state_machine[state][this_event]
        state_event_queue.append(state + '.enter')
      print this_event, state
      print timestamp-starttimestamp, total_loops, total_loops/float(timestamp - starttimestamp)      
    else:
      #time.sleep(0.001)
      #time.sleep(tick_interval)
      default_sleep(tick_interval)
      
  #print state_events
  quit_devices(devices)
  if error:
    print 'There were errors'  
 
    
def start_experiment_server(ExperimentName, StateMachine, DeviceDefinitions):
  """Entry point to call from our experiment script."""
  options, args = parse_command_line_args()
  setup_logging(options)
  expt_def, error = instantiate_experiment(StateMachine, DeviceDefinitions)
  if not error:
    error = initialize_devices(options, expt_def)
  if not error:
    server_loop(options, expt_def)
  else:
    print 'There were errors setting up. Please check logging file ' + options.log_file
