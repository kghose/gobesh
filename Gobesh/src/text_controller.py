# Echo client program

from multiprocessing.connection import Client

address = ('localhost', 6000)
conn = Client(address, authkey='gobesh controller')
    
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