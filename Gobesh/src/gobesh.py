#!/usr/bin/env python
"""Gobesh server. Run with -h to get help. i.e

python gobesh.py -h"""

from optparse import OptionParser
import logging
import time #For the sleep function

import sys
sys.path.append('./Modules/') #Where all the modules live

logger = logging.getLogger('Gobesh')

def initialize_global_variables(GVD):
  """Turns global variable definitions into a list for quicker access.
  Might make this more sophisticated?"""
  GV = []
  key_list = GVD.keys()
  for key in key_list:
    GV.append(GVD[key])
  return GV, key_list

#Need to work out initialization variables
def initialize_devices(DeviceDefinitions, key_list):
  error = False
  DeviceList = {}
  for dev_key in DeviceDefinitions.keys():
    this_device = None
    if DeviceDefinitions[dev_key].has_key('class'):
      this_device = eval(DeviceDefinitions[dev_key]['class'] + '()')
      this_device.initialize(GV)#Need to fix variable passing      
    else:
      error = True
      logger.error('Device %s has no class definition' %(dev_key))

    input_var_idx_list = []    
    if DeviceDefinitions[dev_key].has_key('input variables'):
      input_keys = DeviceDefinitions[dev_key]['input variables']
      if input_keys is not None:
        for var_key in input_keys:
          try:    
            key_idx = key_list.index(var_key)
            input_var_idx_list.append(key_idx)
          except ValueError:
            logger.error('Device %s wants non existent variable %s for input' %(dev_key, var_key))        
    else:
      error = True
      logger.error('Device %s has no input variable definition' %(dev_key))
      
    output_var_idx_list = []    
    if DeviceDefinitions[dev_key].has_key('output variables'):
      ouput_keys = DeviceDefinitions[dev_key]['output variables']
      if ouput_keys is not None:
        for var_key in ouput_keys:
          try:    
            key_idx = key_list.index(var_key)
            output_var_idx_list.append(key_idx)
          except ValueError:
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
       
    DeviceList[dev_key] = [this_device, input_var_idx_list, output_var_idx_list, input_event_list]
  
  return DeviceList, error

def quit_devices(DeviceList):
  for key in DeviceList.keys():
    DeviceList[key][0].quit() #TODO: Gotta fix state_event and variables
  

def poll_devices(DeviceList, timestamp, state_event, GV):
  device_events = []
  for key in DeviceList.keys():
    this_device = DeviceList[key]
    state_event_for_this_device = None
    for event_conns in this_device[3]:
      if state_event in event_conns[1]:
        state_event_for_this_device = event_conns[0]
    
    input_variables = []
    for idx in this_device[1]:
      input_variables.append(GV[idx])
      
    this_event, output_variables = this_device[0].poll(timestamp, state_event_for_this_device, input_variables) #Gotta fix state_event and variables

    #But what if only a subset of outputs are returned?
    if output_variables is not None:
      for n, idx in enumerate(this_device[2]):
        GV[idx] = output_variables[n]
    
    if this_event is not None:
      device_events.append(key + '.' + this_event)
  return device_events


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
                  help="Server tick rate. How many times will the server poll its devices and update the statemachine per second [%default]")

(options, args) = parser.parse_args()

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

tick_interval = 1.0/options.server_tick_rate#Server tick rate

#Load the experiment file and execute its code to setup the state machine and
#the devices
exec open(options.experiment_file)
#print StateMachine

#device_event = ['controller.go', 'setuptrial.done', 'fixation.fixate', 
#                'fixdurationtimer.done','intertrialwait.done','setuptrial.done',
#                'controller.abort','abort.done','controller.quit'] #Events emitted by device
device_events = []
state_events = [] #Events emitted by states
GV, GV_keys = initialize_global_variables(GlobalVariableDefinitions)
print GV
DeviceList, dev_error = initialize_devices(DeviceDefinitions, GV_keys)


error = False #TODO proper error checking

timestamp = 0

state = 'Wait' #Built in start state
while state != 'Exit' and not error: #last state
  #Poll devices
  if len(state_events) > 0:
    this_state_event = state_events.pop(0)
  else:
    this_state_event = None
  
  these_device_events = poll_devices(DeviceList, timestamp, this_state_event, GV)
  if len(these_device_events) > 0:
    device_events += these_device_events
  if len(device_events) > 0:
    this_event = device_events.pop(0)    
    if StateMachine[state].has_key(this_event):
      state_events.append(state + '.exit')
      state = StateMachine[state][this_event]
      state_events.append(state + '.enter')
    print this_event, state
  else:
    time.sleep(tick_interval)

#print state_events
quit_devices(DeviceList)
if error:
  print 'There were errors'