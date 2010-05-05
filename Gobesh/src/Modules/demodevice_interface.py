# Echo client program

from multiprocessing.connection import Client

address = ('localhost', 6001)
conn = Client(address, authkey='gobesh demo')
    
keep_running = True
while keep_running:
  msg=raw_input('Enter string')
  conn.send(msg)
  if msg=='quit':
    keep_running = False

#Wait until the listener says bye
while not conn.poll():
  pass
conn.recv()