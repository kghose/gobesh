"""An example experiment file to use as a reference when building our 
experiments.
This requires you to have the following extra modules installed:
matplotlib + numpy
pyglet

The state machine is described as

wait ---controller.quit---> quit

The devices are:

gcontroller
inputs - None
outputs - None
input events - None
output events - go, abort, quit

avkm
inputs - None
outputs - None
input events - None
output events - None
"""
#States are Sentence case, no spaces
#Devices are all lower case, no spaces
#Event from a device is device name . (dot) event name
import sys
sys.path.append('./Devices/') #Where all the devices live

import gcontroller
import avkm

"""A descriptive name for the experiment."""
ExperimentName = 'AVKM demo experiment'

"""State machine definition:
For the outer dictionary, the key is the state name. 
For the inner dictionary the key is the device event in the form of
device.event, the value is the next state that event will trigger """
StateMachine = {
'Wait': {'controller.quit':'Exit'}}

"""Device definitions: 
For the outer dictionary, the key is the device name. These names must match
up with the names used in the StateMachine definition for the event transitions.
The name __NODEVICE__ is reserved and should not be used as a device name

The inner dictionary must contain the following entries:
'class' - the name of the class to be invoked for the device. It should be the
          module name, followed by the class name. Don't forget to put an 
          'import' statement at the top of the file
'input events' - a dictionary. Each key is a string corresponding to an event
                 the device understands. The value is a list of state events
                 that should trigger this device event. State events are defined
                 as:  statename.enter OR statename.exit
                 statenames must match the state names used in StateMachine
                 definition
'input variables' - a list of variable names and what they are connected to."""
DeviceDefinitions = {
'controller': {'class':'gcontroller.GController',
               'input events':None,
               'input variables':None,
               'output variables':None},
'avkm': {'class':'avkm.GAVKMDevice',
               'input events':None,
               'input variables':None,
               'output variables':None}}