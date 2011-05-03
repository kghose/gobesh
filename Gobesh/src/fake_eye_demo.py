#Uses gfakeeye to generate fake eye position data
import sys
sys.path.append('./Modules/') #Where all the modules live

import gcontroller
import gfakeeye

"""A descriptive name for the experiment."""
ExperimentName = 'Basic demo experiment'

"""Keys are the variable name and the values are the initially loaded values.
These values are overwritten by the values in the experiment configuration file."""
GlobalVariableDefinitions = {'A':1,'B':1}

"""For the outer dictionary, the key is the state name. 
For the inner dictionary the key is the device event in the form of
device.event, the value is the next state that event will trigger """
StateMachine = {
'Wait': {'controller.go':'State1',
         'controller.quit':'Exit'},
'State1': {'demo.eventout1':'State2',
           'demo.eventout2':'State3',
           'controller.abort':'Wait'},
'State2': {'demo.eventout1':'State1',
           'demo.eventout2':'State3',
           'controller.abort':'Wait'},
'State3': {'demo.eventout1':'State2',
           'demo.eventout2':'State1',
           'controller.abort':'Wait'}}

"""For the outer dictionary, the key is the device name. These names must match
up with the names used in the StateMachine definiton.
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
'input variables' - a list of variable names. These names must be a subset of 
                    the GlobalVariableDefinitions
'output variables' - a list of variable names. These names must be a subset of 
                     the GlobalVariableDefinitions"""
DeviceDefinitions = {
'controller': {'class':'gcontroller.GController',
               'input events':None,
               'input variables':None,
               'output variables':None},
'demo': {'class':'gdemodevice.GDemoDevice',
         'input events': {'eventin1':['State2.enter'],
                          'eventin2':['State1.enter','State3.exit']},
         'input variables':['A','B'],
         'output variables': ['A', 'B']}}

