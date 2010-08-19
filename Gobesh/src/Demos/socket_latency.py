"""Server part for demonstrating how to compute average latency for sending
messages back and forth.

An example usage (on the same machine) is to open two shells and then in one
run the server:
python socket_latency.py

In the other run the client:
python socket_latency.py -m'client'

You can also run the client on a different machine:
python socket_latency.py -m'client' -s'<server's address here>'

"""
from optparse import OptionParser
import multiprocessing.connection as mpc
import time


def ping(conn):
  """Ping the connection and tell us the average round trip in us."""
  tsend = time.time()
  conn.send(tsend)
  while not conn.poll():
    pass
  trecv = time.time()    
  conn.recv()
  ttrip_us = (trecv - tsend)/2.0
  return ttrip_us
    
def run_server():
  listener = mpc.Listener(('', 6000), authkey='cs')
  remote_conn = listener.accept()
  print('Connection accepted from:' + listener.last_accepted[0] + ':%d' %(listener.last_accepted[1]))

  cycles_to_do = 1000
  latency_total_us = 0
  for n in range(cycles_to_do):
    latency_total_us += ping(remote_conn)
  print ['Average latency ',  float(latency_total_us)/cycles_to_do*1e6, ' us']
  remote_conn.send('quit')
  
def run_client(server_add = 'localhost'):
  address = (server_add, 6000)#address = ('', 6000)
  conn = mpc.Client(address, authkey='cs')
  keep_running = True
  while keep_running:
    if conn.poll():
      msg = conn.recv()
      conn.send('')#Send a dummy message back as quick as can be
      if msg == 'quit':
        keep_running = False

parser = OptionParser(version="%prog 1.0")
parser.add_option("-m", "--mode", 
                  dest="mode", default="server",
                  help="Set mode: 'server' or 'client' [%default]")
parser.add_option("-s", "--server_add", 
                  dest="server_add", default="localhost",
                  help="Server address (only needed for client) [%default]")

(options, args) = parser.parse_args()

if options.mode == 'server':
  run_server()
elif options.mode == 'client':
  run_client(options.server_add)
