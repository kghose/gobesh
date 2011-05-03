#Front end for demo device
from multiprocessing.connection import Client
import sys
sys.path.append('./Modules/') #Where all the modules live
import keyboard

address = ('localhost', 6001)
conn = Client(address, authkey='gobesh demo')
print 'Got connection to demodevice hook'
print '(1) Event 1'
print '(2) Event 2'
print '(3) Print variables'
    
keep_running = True
while keep_running:
  c = keyboard.getkey()
  if c == '1':
    msg = '1'
  elif c == '2':
    msg = '2'
  elif c == '3':
    msg = '3'
  else:
    msg = None
  try:
    if msg is not None:
      conn.send(msg)
  except:
    print 'Connection lost'
    keep_running = False