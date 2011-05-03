"""An example experiment file to use as a reference when building our 
experiments.
This requires you to have the following extra modules installed:
matplotlib + numpy
pyglet

The state machine is described as

wait ---controller.go---> show fix
     ---controller.quit---> quit
      
show fix ---fixate.fixate---> fixating
         ---pretimer.done---> failed
         ---controller.abort--> wait
         
fixating ---fixate.nofixate---> broke
         ---fixtimer.done---> correct
         ---controller.abort---> wait
         
failed ---posttimer.done---> show fix
       ---controller.abort---> wait

broke ---posttimer.done---> show fix
      ---controller.abort---> wait

correct ---posttimer.done---> show fix
        ---controller.abort---> wait

The devices are

gcontroller 

gplot 

gfakeeye 

gfixate

trialend

The only experiment specific module here is the trialend module which saves
trial data to a file




"""
#States are Sentence case, no spaces
#Devices are all lower case, no spaces
#Event from a device is device name . (dot) event name
import sys
sys.path.append('./Modules/') #Where all the modules live

import gcontroller
import gdemodevice
import gvisualdevice

"""A descriptive name for the experiment."""
ExperimentName = 'Basic demo experiment'

"""State machine definition:
For the outer dictionary, the key is the state name. 
For the inner dictionary the key is the device event in the form of
device.event, the value is the next state that event will trigger """
StateMachine = {
'Wait': {'controller.go':'State1',
         'controller.quit':'Exit'},
'State1': {'demo1.eventout1':'State2',
           'demo1.eventout2':'State3',
           'controller.abort':'Wait'},
'State2': {'demo1.eventout1':'State3',
           'demo1.eventout2':'State1',
           'controller.abort':'Wait'},
'State3': {'demo1.eventout1':'State1',
           'demo1.eventout2':'State2',
           'controller.abort':'Wait'}}

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
#'demo1': {'class':'gdemodevice.GDemoDevice',
#         'input events': {'eventin1':['State1.enter'],
#                          'eventin2':['State1.enter','State2.enter']},
#         'input variables':{'a':'demo2.y',
#                            'b':'demo2.x'}},
'demo1': {'class':'gdemodevice.GDemoDevice',
         'input events': {'eventin1':['State1.enter'],
                          'eventin2':['State1.enter','State2.enter']},
         'input variables':{'a':'demo2.y',
                            'b':'demo2.x'}},
'demo2': {'class':'gdemodevice.GDemoDevice',
         'input events': {'eventin1':['State2.enter'],
                          'eventin2':['State3.enter']},
         'input variables':{'a':'demo1.y',
                            'b':'demo1.x'}}}