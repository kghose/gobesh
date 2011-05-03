import logging
import time
import sys
sys.path.append('Modules')
import templatemodule

def initialize(data_space):
  data_space['state'] = 'Pretrial'
  
  



LOG_FILENAME = 'gobesh.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)  

data_space = {}

initialize(data_space)
state = data_space['state']
while state != 'Quit':
  get_data_from_sources(data_space)
  supply_data_to_sinks(data_space)
  receive_commands(data_space)
  poll_monitors(data_space)
  
  









mydev = templatemodule.Device('Kaushik')
parent_conn, p = mydev.handles()
p.start()

print 'Waiting for 2 sec after starting device'
time.sleep(2)

msg = {'command':'start'}  
parent_conn.send(msg)
print 'Trying to start device'

time.sleep(4)
while parent_conn.poll():
  msg = parent_conn.recv()
  print msg

msg = {'command':'quit'}  
parent_conn.send(msg)
print 'Trying to quit device'

p.join()