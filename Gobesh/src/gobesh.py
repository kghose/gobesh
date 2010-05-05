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
  error = False
  GV = {}
  for key in GVD.keys():
    GV[key] = GVD[key]
  return GV, error

#Need to work out initialization variables
def initialize_devices(DeviceDefinitions, GV):
  error = False
  DeviceList = {}
  for key in DeviceDefinitions.keys():
    if DeviceDefinitions[key].has_key('class'):
      DeviceList[key] = eval(DeviceDefinitions[key]['class'] + '()')
      DeviceList[key].initialize(GV)#Need to fix variable passing      
    else:
      error = True
      logger.error('Device %s has class definition' %(key))
  return DeviceList, error

def quit_devices(DeviceList):
  for key in DeviceList.keys():
    DeviceList[key].quit() #Gotta fix state_event and variables
  

def poll_devices(DeviceList, timestamp, state_events, GV):
  device_events = []
  for key in DeviceList.keys():
    input_variables = [GV['A'], GV['B']]
    this_event, output_variables = DeviceList[key].poll(timestamp, [], input_variables) #Gotta fix state_event and variables
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
GV, var_error = initialize_global_variables(GlobalVariableDefinitions)
DeviceList, dev_error = initialize_devices(DeviceDefinitions, GV)
error = False #TODO proper error checking

timestamp = 0

state = 'Wait' #Built in start state
while state != 'Exit' and not error: #last state
  #Poll devices
  these_device_events = poll_devices(DeviceList, timestamp, state_events, GV)
  if len(these_device_events) > 0:
    device_events += these_device_events
  if len(device_events) > 0:
    this_event = device_events.pop(0)    
    if StateMachine[state].has_key(this_event):
      state_events.append(state + '.exit')
      state = StateMachine[state][this_event]
      state_events.append(state + '.enter')
    print this_event, state
  time.sleep(tick_interval)

#print state_events
quit_devices(DeviceList)
if error:
  print 'There were errors'



#modu1.run()
#print 'Ha'

#logger.debug('This is a debug message')
#logger.info('This is an info message')
#logger.warning('This is a warning message')
#logger.error('This is an error message')
#logger.critical('This is a critical error message')
