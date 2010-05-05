#States are Sentence case, no spaces
#Devices are all lower case, no spaces
#Event from a device is device name . (dot) event name

import gcontroller
import gdemodevice

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

GlobalVariableDefinitions = {'A':1,'B':1}