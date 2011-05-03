#A simple text based controller for Gobesh
from multiprocessing.connection import Client
import sys
sys.path.append('./Modules/') #Where all the modules live
import keyboard

address = ('localhost', 6000)#('dhc016970.med.harvard.edu', 6000)
conn = Client(address, authkey='gobesh controller')
print 'Got connection to server'
print '(g)o'
print '(a)bort'
print '(q)uit'
    
keep_running = True
while keep_running:
  c = keyboard.getkey()
  if c == 'g':
    msg = 'go'
  elif c == 'a':
    msg = 'abort'
  elif c == 'q':
    msg = 'quit'
  else:
    msg = None
  try:
    if msg is not None:
      conn.send(msg)
  except:
    print 'Connection lost'
    keep_running = False